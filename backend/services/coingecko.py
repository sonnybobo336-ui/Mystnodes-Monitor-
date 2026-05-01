"""CoinGecko price client with retry/backoff and Mongo TTL cache."""
import asyncio
import time
from typing import Any, Dict
import httpx

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
COINS = ["bitcoin", "ethereum", "solana", "mysterium"]
SYMBOL_MAP = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "mysterium": "MYST"}

_cache: Dict[str, Any] = {"data": None, "ts": 0}
CACHE_TTL = 45  # seconds


async def fetch_prices() -> Dict[str, Any]:
    """Fetch live prices with retry. Returns dict shaped for the frontend."""
    now = time.time()
    if _cache["data"] and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["data"]

    params = {
        "ids": ",".join(COINS),
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
    }
    headers = {"User-Agent": "NodeForge/1.0", "Accept": "application/json"}
    last_err = None
    async with httpx.AsyncClient(timeout=15, headers=headers) as client:
        for attempt in range(4):
            try:
                r = await client.get(f"{COINGECKO_BASE}/simple/price", params=params)
                if r.status_code == 200:
                    raw = r.json()
                    out = []
                    for cid in COINS:
                        d = raw.get(cid, {})
                        out.append({
                            "id": cid,
                            "symbol": SYMBOL_MAP[cid],
                            "price_usd": d.get("usd"),
                            "change_24h_pct": d.get("usd_24h_change"),
                            "market_cap_usd": d.get("usd_market_cap"),
                        })
                    result = {"prices": out, "as_of": now}
                    _cache["data"] = result
                    _cache["ts"] = now
                    return result
                last_err = f"{r.status_code}"
            except Exception as e:
                last_err = str(e)
            await asyncio.sleep(1.5 ** attempt)
    # Return stale or empty
    if _cache["data"]:
        return _cache["data"]
    return {"prices": [], "as_of": now, "error": f"CoinGecko unavailable: {last_err}"}
