"""Aggregate snapshots from all sources for the dashboard and AI."""
import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from services import coingecko, mystnodes, tailscale, wallets


def _wallets() -> List[str]:
    return [a.strip() for a in os.environ.get("WALLET_ADDRESSES", "").split(",") if a.strip()]


def _node_keys() -> List[str]:
    return [k.strip() for k in os.environ.get("MYST_NODE_KEYS", "").split(",") if k.strip()]


async def _safe(name: str, coro):
    try:
        return name, await coro
    except Exception as e:
        return name, {"_error": str(e)}


async def get_snapshot(include_ai: bool = False) -> Dict[str, Any]:
    """Fetch everything in parallel; return a single snapshot dict."""
    tasks = [
        _safe("prices", coingecko.fetch_prices()),
        _safe("wallet_balances", wallets.get_balances(_wallets())),
    ]
    # Mystnodes
    myst_client = mystnodes.get_client()
    if myst_client:
        tasks.append(_safe("mystnodes", myst_client.list_nodes()))
    else:
        tasks.append(_safe("mystnodes", _placeholder_mystnodes()))
    # Tailscale
    ts_key = os.environ.get("TAILSCALE_API_KEY", "").strip()
    ts_net = os.environ.get("TAILSCALE_TAILNET", "-").strip() or "-"
    if ts_key:
        tasks.append(_safe("tailscale", tailscale.list_devices(ts_key, ts_net)))
    else:
        tasks.append(_safe("tailscale", _placeholder_tailscale()))

    results = await asyncio.gather(*tasks)
    snapshot: Dict[str, Any] = {name: data for name, data in results}
    snapshot["as_of"] = datetime.now(timezone.utc).isoformat()
    snapshot["config"] = {
        "mystnodes_connected": myst_client is not None,
        "tailscale_connected": bool(ts_key),
        "node_keys_configured": _node_keys(),
        "wallet_addresses": _wallets(),
    }
    snapshot["derived"] = compute_derived(snapshot)
    return snapshot


async def _placeholder_mystnodes():
    return {
        "_not_connected": True,
        "hint": "Connect Mystnodes account in Settings to enable node metrics.",
    }


async def _placeholder_tailscale():
    return {
        "_not_connected": True,
        "hint": "Connect Tailscale API key in Settings to map node hosts.",
    }


def compute_derived(snap: Dict[str, Any]) -> Dict[str, Any]:
    """Compute KPIs from raw snapshot."""
    out: Dict[str, Any] = {
        "earnings_24h_myst": 0.0,
        "earnings_30d_myst": 0.0,
        "earnings_lifetime_myst": 0.0,
        "earnings_settled_myst": 0.0,
        "earnings_unsettled_myst": 0.0,
        "projected_annual_myst": 0.0,
        "avg_uptime_pct": 0.0,
        "nodes_total": 0,
        "nodes_online": 0,
        "nodes_offline": 0,
    }
    nodes = snap.get("mystnodes")
    if isinstance(nodes, list):
        out["nodes_total"] = len(nodes)
        uptime_minutes_total = 0
        for n in nodes:
            status = (n.get("nodeStatus") or {})
            online = bool(status.get("online"))
            out["nodes_online"] += 1 if online else 0
            out["nodes_offline"] += 0 if online else 1
            # Earnings 24h: sum etherAmount across services
            for e in (n.get("earnings") or []):
                try:
                    out["earnings_24h_myst"] += float(e.get("etherAmount", 0))
                except Exception:
                    pass
            life = n.get("lifetimeEarnings") or {}
            try:
                out["earnings_lifetime_myst"] += float(life.get("totalEther", 0))
            except Exception:
                pass
            try:
                out["earnings_settled_myst"] += float(life.get("settledEther", 0))
                out["earnings_unsettled_myst"] += float(life.get("unsettledEther", 0))
            except Exception:
                pass
            try:
                uptime_minutes_total += int(n.get("uptimeMinLast24H", 0))
            except Exception:
                pass
        if out["nodes_total"] > 0:
            out["avg_uptime_pct"] = round(min(100.0, (uptime_minutes_total / (out["nodes_total"] * 1440)) * 100), 1)
        out["earnings_30d_myst"] = max(out["earnings_24h_myst"] * 30.0, out["earnings_lifetime_myst"])
        out["projected_annual_myst"] = out["earnings_24h_myst"] * 365.0
    # USD conversion
    myst_price = 0.0
    prices = snap.get("prices", {})
    if isinstance(prices, dict):
        for p in (prices.get("prices") or []):
            if p.get("id") == "mysterium":
                myst_price = p.get("price_usd") or 0.0
                break
    out["myst_price_usd"] = myst_price
    out["earnings_24h_usd"] = round(out["earnings_24h_myst"] * myst_price, 2)
    out["earnings_30d_usd"] = round(out["earnings_30d_myst"] * myst_price, 2)
    out["earnings_lifetime_usd"] = round(out["earnings_lifetime_myst"] * myst_price, 2)
    out["projected_annual_usd"] = round(out["projected_annual_myst"] * myst_price, 2)
    return out
