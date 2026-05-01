"""
NodeForge POC v2 — fixed integrations.
"""
import asyncio, json, os, sys, traceback, re
from pathlib import Path
from typing import Any, Dict, List
import httpx
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
TAILSCALE_API_KEY = os.environ.get("TAILSCALE_API_KEY", "")
TAILSCALE_TAILNET = os.environ.get("TAILSCALE_TAILNET", "-")
WALLET_ADDRESSES = [a.strip() for a in os.environ.get("WALLET_ADDRESSES", "").split(",") if a.strip()]

COINGECKO_IDS = "bitcoin,ethereum,solana,mysterium"
MYST_POLYGON_CONTRACT = "0x1379E8886A944d2D9d440b3d88DF536Aea08d9F3"  # MYST on Polygon


# ---------- CoinGecko (with retry/backoff) ----------
async def test_coingecko() -> Dict[str, Any]:
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": COINGECKO_IDS,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
    }
    last_err = None
    async with httpx.AsyncClient(timeout=20, headers={"User-Agent": "NodeForge/1.0", "Accept": "application/json"}) as client:
        for attempt in range(4):
            try:
                r = await client.get(url, params=params)
                if r.status_code == 200:
                    data = r.json()
                    assert "bitcoin" in data, f"missing tokens: {data}"
                    print(f"[OK] CoinGecko: {json.dumps(data)[:300]}")
                    return data
                last_err = f"{r.status_code} {r.text[:200]}"
            except Exception as e:
                last_err = str(e)
            await asyncio.sleep(2 ** attempt)
    raise RuntimeError(f"CoinGecko failed after retries: {last_err}")


# ---------- Mysterium Quality Oracle (correct endpoints) ----------
async def test_mystnodes() -> Dict[str, Any]:
    base = "https://quality.mysterium.network/api/v3"
    results: Dict[str, Any] = {"providers": {}}
    headers = {"User-Agent": "NodeForge/1.0", "Accept": "application/json"}

    async with httpx.AsyncClient(timeout=25, headers=headers) as client:
        for pid in WALLET_ADDRESSES:
            pid_lc = pid.lower()
            provider_data: Dict[str, Any] = {"provider_id": pid_lc, "calls": {}}

            # Real endpoints from openapi: /provider/<x> with provider_id query param
            calls = [
                ("sessions_30d",      f"{base}/provider/sessions",         {"range": "30d", "provider_id": pid_lc}),
                ("sessions_count_30d",f"{base}/provider/sessions-count",   {"range": "30d", "provider_id": pid_lc}),
                ("series_earnings",   f"{base}/provider/series-earnings",  {"range": "30d", "provider_id": pid_lc}),
                ("series_sessions",   f"{base}/provider/series-sessions",  {"range": "30d", "provider_id": pid_lc}),
                ("series_data",       f"{base}/provider/series-data",      {"range": "30d", "provider_id": pid_lc}),
                ("service_earnings",  f"{base}/provider/service-earnings", {"range": "30d", "provider_id": pid_lc}),
                ("activity_stats",    f"{base}/provider/activity-stats",   {"range": "30d", "provider_id": pid_lc}),
                ("transferred_data",  f"{base}/provider/transferred-data", {"range": "30d", "provider_id": pid_lc}),
                ("statuses",          f"{base}/provider/statuses",         {"provider_id": pid_lc}),
                ("quality",           f"{base}/provider/quality",          {"provider_id": pid_lc}),
            ]
            for label, url, params in calls:
                try:
                    r = await client.get(url, params=params)
                    if r.status_code == 200:
                        try:
                            payload = r.json()
                        except Exception:
                            payload = {"raw": r.text[:300]}
                        provider_data["calls"][label] = payload
                    else:
                        provider_data["calls"][label] = {"_status": r.status_code, "_body": r.text[:200]}
                except Exception as e:
                    provider_data["calls"][label] = {"_error": str(e)}
            results["providers"][pid_lc] = provider_data

    print(f"[OK] Mysterium provider data fetched. Sample for {WALLET_ADDRESSES[0][:10]}…:")
    first_pid = WALLET_ADDRESSES[0].lower()
    print(json.dumps(results["providers"][first_pid]["calls"], indent=2)[:2000])
    return results


# ---------- Tailscale (gracefully optional) ----------
async def test_tailscale() -> Dict[str, Any]:
    if not TAILSCALE_API_KEY:
        return {"_skipped": "no TAILSCALE_API_KEY"}
    headers = {"Authorization": f"Bearer {TAILSCALE_API_KEY}"}
    url = f"https://api.tailscale.com/api/v2/tailnet/{TAILSCALE_TAILNET}/devices"
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        r = await client.get(url)
        if r.status_code != 200:
            r2 = await client.get(url, auth=(TAILSCALE_API_KEY, ""))
            if r2.status_code == 200:
                r = r2
            else:
                # NOT fatal - return informative error structure for UI
                return {
                    "_error": f"Tailscale auth failed ({r.status_code}). Token may not be a valid 'tskey-api-...' API access token.",
                    "_hint": "Generate a new API access token at https://login.tailscale.com/admin/settings/keys with 'devices:core' scope.",
                    "_status": r.status_code,
                }
        data = r.json()
    devices = data.get("devices", [])
    summary = [
        {
            "id": d.get("id"),
            "name": d.get("name") or d.get("hostname"),
            "addresses": d.get("addresses"),
            "os": d.get("os"),
            "lastSeen": d.get("lastSeen"),
        }
        for d in devices
    ]
    print(f"[OK] Tailscale: {len(devices)} device(s)")
    return {"count": len(devices), "devices": summary}


# ---------- Wallet balances: ETH mainnet + MYST on Polygon ----------
async def test_wallet_balances() -> Dict[str, Any]:
    eth_rpc = "https://eth.llamarpc.com"
    polygon_rpc = "https://polygon-rpc.com"
    out: Dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=20) as client:
        for addr in WALLET_ADDRESSES:
            entry = {}
            # ETH balance
            try:
                r = await client.post(eth_rpc, json={"jsonrpc":"2.0","method":"eth_getBalance","params":[addr,"latest"],"id":1})
                wei = int(r.json().get("result","0x0"), 16)
                entry["eth"] = wei / 10**18
            except Exception as e:
                entry["eth_error"] = str(e)
            # POL (MATIC) native balance on Polygon
            try:
                r = await client.post(polygon_rpc, json={"jsonrpc":"2.0","method":"eth_getBalance","params":[addr,"latest"],"id":1})
                wei = int(r.json().get("result","0x0"), 16)
                entry["pol"] = wei / 10**18
            except Exception as e:
                entry["pol_error"] = str(e)
            # MYST (ERC20 on Polygon) balance via eth_call(balanceOf)
            try:
                # balanceOf(address) selector = 0x70a08231
                addr_padded = addr.lower().replace("0x","").rjust(64, "0")
                data_hex = "0x70a08231" + addr_padded
                r = await client.post(polygon_rpc, json={
                    "jsonrpc":"2.0","method":"eth_call",
                    "params":[{"to": MYST_POLYGON_CONTRACT, "data": data_hex}, "latest"],
                    "id":1,
                })
                hex_result = r.json().get("result", "0x0")
                bal = int(hex_result, 16) / 10**18  # MYST has 18 decimals
                entry["myst"] = bal
            except Exception as e:
                entry["myst_error"] = str(e)
            out[addr] = entry
    print(f"[OK] Wallet balances: {json.dumps(out)[:400]}")
    return out


# ---------- Emergent LLM (Claude Sonnet 4.5) ----------
async def test_llm(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    if not EMERGENT_LLM_KEY:
        raise RuntimeError("Missing EMERGENT_LLM_KEY")
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    system = (
        "You are NodeForge AI, an analyst for crypto node operations (Mysterium dVPN nodes). "
        "Given a snapshot, return STRICT JSON ONLY with this shape:\n"
        '{ "underperformers": [{"id": str, "reason": str}], '
        '"revenue_loss_estimate_usd": number, '
        '"recommendations": [str], '
        '"summary": str }\n'
        "No markdown, no prose, JSON only."
    )
    chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id="nodeforge-poc",
                   system_message=system).with_model("anthropic", "claude-sonnet-4-5-20250929")

    # Trim snapshot for prompt
    compact = json.dumps(snapshot, default=str)[:5000]
    raw = await chat.send_message(UserMessage(text=f"Snapshot:\n{compact}\n\nReturn JSON."))
    text = (raw or "").strip().strip("`")
    if text.lower().startswith("json"):
        text = text[4:].strip()
    try:
        parsed = json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        parsed = json.loads(m.group(0)) if m else {"raw": text[:500]}
    print(f"[OK] Claude AI: {json.dumps(parsed)[:500]}")
    return parsed


async def main() -> int:
    snapshot: Dict[str, Any] = {}
    failures: List[str] = []
    for name, fn in [
        ("coingecko", test_coingecko),
        ("mystnodes", test_mystnodes),
        ("tailscale", test_tailscale),
        ("wallets", test_wallet_balances),
    ]:
        try:
            snapshot[name] = await fn()
        except Exception as e:
            failures.append(name)
            print(f"[FAIL] {name}: {e}"); traceback.print_exc()
            snapshot[name] = {"_error": str(e)}

    try:
        snapshot["ai"] = await test_llm(snapshot)
    except Exception as e:
        failures.append("llm"); print(f"[FAIL] llm: {e}"); traceback.print_exc()

    # Tailscale auth fail is non-fatal (treated as optional)
    fatal = [f for f in failures if f != "tailscale"]
    if "tailscale" in failures and isinstance(snapshot.get("tailscale"), dict) and "_error" in snapshot["tailscale"]:
        pass
    print("\n=========== FINAL SNAPSHOT ===========")
    print(json.dumps(snapshot, default=str, indent=2)[:6000])
    if fatal:
        print(f"\n[FATAL FAILURES: {fatal}]")
        return 1
    if failures:
        print(f"\n[NON-FATAL ISSUES: {failures} - dashboard will degrade gracefully]")
    print("\n[POC OK]"); return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
