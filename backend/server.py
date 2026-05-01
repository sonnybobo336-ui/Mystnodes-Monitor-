"""NodeForge backend — FastAPI app with /api routes."""
import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.cors import CORSMiddleware

from services import ai as ai_service
from services import coingecko, mystnodes, scheduler, tailscale, wallets
from services.aggregator import compute_derived, get_snapshot

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="NodeForge API")
api = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("nodeforge")

# ----- Helpers -----

async def _save_settings(doc: Dict[str, Any]) -> None:
    await db.settings.update_one({"_id": "main"}, {"$set": doc}, upsert=True)


async def _load_settings() -> Dict[str, Any]:
    doc = await db.settings.find_one({"_id": "main"}) or {}
    doc.pop("_id", None)
    return doc


async def _bootstrap_clients_from_settings() -> None:
    """On startup, load saved credentials from Mongo and wire up clients."""
    settings = await _load_settings()
    myst_email = settings.get("mystnodes_email") or os.environ.get("MYSTNODES_EMAIL")
    myst_pw = settings.get("mystnodes_password") or os.environ.get("MYSTNODES_PASSWORD")
    if myst_email and myst_pw:
        mystnodes.configure(myst_email, myst_pw)
    ts_key = settings.get("tailscale_api_key")
    if ts_key:
        os.environ["TAILSCALE_API_KEY"] = ts_key
    ts_net = settings.get("tailscale_tailnet")
    if ts_net:
        os.environ["TAILSCALE_TAILNET"] = ts_net


# ===== Models =====
class TestMystnodesRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    email: str
    password: str


class TestTailscaleRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    api_key: str
    tailnet: Optional[str] = "-"


class SaveSettingsRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    mystnodes_email: Optional[str] = None
    mystnodes_password: Optional[str] = None
    tailscale_api_key: Optional[str] = None
    tailscale_tailnet: Optional[str] = None
    auto_withdrawal_days: Optional[int] = None
    auto_withdrawal_threshold_myst: Optional[float] = None


# ===== Routes =====
@api.get("/")
async def root():
    return {"name": "NodeForge", "status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@api.get("/prices")
async def get_prices():
    return await coingecko.fetch_prices()


@api.get("/wallets")
async def get_wallets():
    addresses = [a.strip() for a in os.environ.get("WALLET_ADDRESSES", "").split(",") if a.strip()]
    return {"addresses": addresses, "balances": await wallets.get_balances(addresses)}


@api.get("/snapshot")
async def get_snapshot_endpoint():
    return await get_snapshot()


@api.get("/nodes")
async def get_nodes():
    snap = await get_snapshot()
    nodes = snap.get("mystnodes")
    if isinstance(nodes, dict) and nodes.get("_not_connected"):
        return {"connected": False, "hint": nodes.get("hint"), "nodes": []}
    if isinstance(nodes, dict) and nodes.get("_error"):
        return {"connected": True, "error": nodes["_error"], "nodes": []}
    # Map tailscale online state by hostname/ip
    devices = snap.get("tailscale")
    device_list = devices if isinstance(devices, list) else []
    out = []
    for n in (nodes or []):
        nid = n.get("identity") or n.get("id")
        ext_ip = n.get("externalIp") or n.get("external_ip")
        match = None
        for d in device_list:
            if not d:
                continue
            addrs = d.get("addresses") or []
            if ext_ip and ext_ip in addrs:
                match = d
                break
            if d.get("name", "").lower().startswith((n.get("name") or "").lower().replace(" ", "-")[:6] or "_x_no"):
                match = d
        out.append({
            "id": nid,
            "name": n.get("name"),
            "identity": n.get("identity"),
            "online": bool((n.get("nodeStatus") or {}).get("online")),
            "service_types": (n.get("nodeStatus") or {}).get("serviceTypes", []),
            "quality": (n.get("nodeStatus") or {}).get("quality"),
            "location": (n.get("nodeStatus") or {}).get("location"),
            "ip_category": (n.get("nodeStatus") or {}).get("ipCategory"),
            "online_last_at": (n.get("nodeStatus") or {}).get("onlineLastAt"),
            "external_ip": ext_ip,
            "isp": n.get("isp"),
            "os": n.get("os"),
            "version": n.get("version"),
            "uptime_min_24h": n.get("uptimeMinLast24H"),
            "earnings_24h": n.get("earnings", []),
            "earnings_24h_myst": sum(float(e.get("etherAmount", 0) or 0) for e in (n.get("earnings") or [])),
            "lifetime_earnings": n.get("lifetimeEarnings") or {},
            "tailscale_device": (
                {
                    "id": match.get("id"),
                    "name": match.get("name"),
                    "addresses": match.get("addresses"),
                    "lastSeen": match.get("lastSeen"),
                    "os": match.get("os"),
                }
                if match else None
            ),
        })
    return {"connected": True, "nodes": out, "count": len(out)}


@api.get("/earnings/summary")
async def earnings_summary():
    snap = await get_snapshot()
    return {"derived": snap.get("derived", {}), "as_of": snap.get("as_of")}


@api.get("/earnings/timeseries")
async def earnings_timeseries(days: int = 30):
    """30-day time series from per-node sessions if available, else synthesized from current run-rate."""
    days = max(1, min(days, 90))
    client = mystnodes.get_client()
    points: List[Dict[str, Any]] = []
    if client:
        try:
            nodes = await client.list_nodes()
            ids = [n.get("identity") for n in nodes if n.get("identity")]
            # Aggregate daily sessions across nodes
            from collections import defaultdict
            daily = defaultdict(float)
            for ident in ids:
                try:
                    sessions = await client.sessions(ident)
                except Exception:
                    sessions = []
                for s in sessions:
                    started = s.get("startedAt") or ""
                    if not started:
                        continue
                    day = started[:10]
                    try:
                        daily[day] += float(s.get("earning", 0) or 0)
                    except Exception:
                        pass
            for day in sorted(daily.keys()):
                points.append({"date": day, "earnings_myst": round(daily[day], 6)})
        except Exception as e:
            logger.warning(f"timeseries fallback: {e}")
    if not points:
        # Synthetic flat line at 0 for empty state
        from datetime import datetime as _dt, timedelta as _td
        today = _dt.now(timezone.utc).date()
        for i in range(days):
            points.append({"date": (today - _td(days=days - 1 - i)).isoformat(), "earnings_myst": 0.0})
    # Add USD using current price
    prices = await coingecko.fetch_prices()
    myst_price = 0.0
    for p in (prices.get("prices") or []):
        if p.get("id") == "mysterium":
            myst_price = p.get("price_usd") or 0.0
            break
    for pt in points:
        pt["earnings_usd"] = round((pt["earnings_myst"] or 0) * myst_price, 4)
    return {"points": points, "myst_price_usd": myst_price}


@api.post("/ai/insights")
async def ai_insights():
    snap = await get_snapshot()
    # Trim heavy lists for prompt size
    light = {
        "prices": snap.get("prices"),
        "derived": snap.get("derived"),
        "wallet_balances": snap.get("wallet_balances"),
        "nodes_summary": _nodes_summary(snap.get("mystnodes")),
        "tailscale_summary": _ts_summary(snap.get("tailscale")),
        "config": snap.get("config"),
        "as_of": snap.get("as_of"),
    }
    insights = await ai_service.generate_insights(light)
    # Persist last insights
    try:
        await db.ai_insights.update_one(
            {"_id": "latest"},
            {"$set": {"insights": insights, "as_of": snap.get("as_of")}},
            upsert=True,
        )
    except Exception:
        pass
    return {"insights": insights, "as_of": snap.get("as_of")}


def _nodes_summary(nodes):
    if not isinstance(nodes, list):
        return nodes
    return [
        {
            "id": n.get("identity"),
            "name": n.get("name"),
            "online": bool((n.get("nodeStatus") or {}).get("online")),
            "service_types": (n.get("nodeStatus") or {}).get("serviceTypes", []),
            "quality": (n.get("nodeStatus") or {}).get("quality"),
            "location": (n.get("nodeStatus") or {}).get("location"),
            "uptime_min_24h": n.get("uptimeMinLast24H"),
            "earnings_24h_myst": sum(float(e.get("etherAmount", 0) or 0) for e in (n.get("earnings") or [])),
            "lifetime": n.get("lifetimeEarnings") or {},
            "isp": n.get("isp"),
        }
        for n in nodes
    ]


def _ts_summary(devs):
    if not isinstance(devs, list):
        return devs
    return [
        {
            "id": d.get("id"),
            "name": d.get("name"),
            "os": d.get("os"),
            "addresses": d.get("addresses"),
            "lastSeen": d.get("lastSeen"),
        }
        for d in devs
    ]


@api.get("/ai/insights/latest")
async def ai_insights_latest():
    doc = await db.ai_insights.find_one({"_id": "latest"}) or {}
    doc.pop("_id", None)
    return doc


# ----- Withdrawal scheduler endpoints -----
@api.get("/withdrawal/state")
async def withdrawal_state():
    state = scheduler.get_state()
    # Recent log
    cursor = db.withdrawal_logs.find({}, {"_id": 0}).sort("created_at", -1).limit(5)
    state["recent"] = [d async for d in cursor]
    return state


@api.post("/withdrawal/run")
async def withdrawal_run():
    note = await scheduler.trigger_now()
    return {"ok": True, "result": note}


@api.get("/withdrawal/log")
async def withdrawal_log(limit: int = 50):
    cursor = db.withdrawal_logs.find({}, {"_id": 0}).sort("created_at", -1).limit(min(max(limit, 1), 200))
    return {"items": [d async for d in cursor]}


# ----- Settings + connection tests -----
@api.get("/settings")
async def get_settings():
    s = await _load_settings()
    return {
        "mystnodes_connected": mystnodes.get_client() is not None,
        "mystnodes_email": s.get("mystnodes_email"),
        "tailscale_connected": bool(os.environ.get("TAILSCALE_API_KEY")),
        "tailscale_tailnet": os.environ.get("TAILSCALE_TAILNET", "-"),
        "auto_withdrawal_days": int(os.environ.get("AUTO_WITHDRAWAL_DAYS", 5)),
        "auto_withdrawal_threshold_myst": float(os.environ.get("AUTO_WITHDRAWAL_THRESHOLD_MYST", 5)),
        "wallet_addresses": [a.strip() for a in os.environ.get("WALLET_ADDRESSES", "").split(",") if a.strip()],
        "node_keys_configured": [k.strip() for k in os.environ.get("MYST_NODE_KEYS", "").split(",") if k.strip()],
    }


@api.post("/settings/save")
async def save_settings(req: SaveSettingsRequest):
    update: Dict[str, Any] = {}
    if req.mystnodes_email is not None:
        update["mystnodes_email"] = req.mystnodes_email
    if req.mystnodes_password is not None and req.mystnodes_password != "":
        update["mystnodes_password"] = req.mystnodes_password
    if req.tailscale_api_key is not None:
        update["tailscale_api_key"] = req.tailscale_api_key
    if req.tailscale_tailnet is not None:
        update["tailscale_tailnet"] = req.tailscale_tailnet
    if req.auto_withdrawal_days is not None:
        update["auto_withdrawal_days"] = int(req.auto_withdrawal_days)
        os.environ["AUTO_WITHDRAWAL_DAYS"] = str(int(req.auto_withdrawal_days))
    if req.auto_withdrawal_threshold_myst is not None:
        update["auto_withdrawal_threshold_myst"] = float(req.auto_withdrawal_threshold_myst)
        os.environ["AUTO_WITHDRAWAL_THRESHOLD_MYST"] = str(float(req.auto_withdrawal_threshold_myst))
    if update:
        await _save_settings(update)
    # Re-bootstrap clients (so changes take effect immediately)
    await _bootstrap_clients_from_settings()
    # Restart scheduler if interval changed
    if req.auto_withdrawal_days is not None:
        scheduler.shutdown()
        scheduler.start(asyncio.get_running_loop())
    return await get_settings()


@api.post("/settings/test/mystnodes")
async def test_mystnodes_endpoint(req: TestMystnodesRequest):
    return await mystnodes.test_credentials(req.email, req.password)


@api.post("/settings/test/tailscale")
async def test_tailscale_endpoint(req: TestTailscaleRequest):
    return await tailscale.test_credentials(req.api_key, req.tailnet or "-")


# ----- App lifecycle -----
@app.on_event("startup")
async def on_startup():
    scheduler.set_db(db)
    await _bootstrap_clients_from_settings()
    try:
        scheduler.start(asyncio.get_running_loop())
    except Exception as e:
        logger.warning(f"scheduler start failed: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    scheduler.shutdown()
    client.close()


app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
