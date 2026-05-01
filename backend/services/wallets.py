"""On-chain wallet balances: ETH mainnet + Polygon (POL + MYST ERC-20)."""
import asyncio
from typing import Any, Dict, List, Optional
import httpx

ETH_RPCS = [
    "https://eth.llamarpc.com",
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com",
]
POLYGON_RPCS = [
    "https://polygon.llamarpc.com",
    "https://rpc.ankr.com/polygon",
    "https://polygon-bor-rpc.publicnode.com",
    "https://polygon-rpc.com",
]
MYST_POLYGON_CONTRACT = "0x1379E8886A944d2D9d440b3d88DF536Aea08d9F3"  # MYST on Polygon


async def _rpc(client: httpx.AsyncClient, urls: List[str], method: str, params: list) -> Any:
    last_err: Optional[str] = None
    for url in urls:
        try:
            r = await client.post(url, json={"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
            if r.status_code == 200:
                data = r.json()
                if "result" in data:
                    return data["result"]
                last_err = data.get("error", {}).get("message", "no result")
            else:
                last_err = f"{r.status_code}"
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(f"All RPCs failed: {last_err}")


async def get_balances(addresses: List[str]) -> List[Dict[str, Any]]:
    """Returns a list of wallet records with eth/pol/myst balances."""
    out: List[Dict[str, Any]] = []
    if not addresses:
        return out
    async with httpx.AsyncClient(timeout=15) as client:
        async def one(addr: str) -> Dict[str, Any]:
            entry: Dict[str, Any] = {"address": addr, "eth": None, "pol": None, "myst": None}
            try:
                wei = int(await _rpc(client, ETH_RPCS, "eth_getBalance", [addr, "latest"]) or "0x0", 16)
                entry["eth"] = wei / 10**18
            except Exception as e:
                entry["eth_error"] = str(e)
            try:
                wei = int(await _rpc(client, POLYGON_RPCS, "eth_getBalance", [addr, "latest"]) or "0x0", 16)
                entry["pol"] = wei / 10**18
            except Exception as e:
                entry["pol_error"] = str(e)
            try:
                addr_padded = addr.lower().replace("0x", "").rjust(64, "0")
                data_hex = "0x70a08231" + addr_padded
                hex_result = await _rpc(client, POLYGON_RPCS, "eth_call", [{"to": MYST_POLYGON_CONTRACT, "data": data_hex}, "latest"]) or "0x0"
                entry["myst"] = int(hex_result, 16) / 10**18
            except Exception as e:
                entry["myst_error"] = str(e)
            return entry
        out = await asyncio.gather(*[one(a) for a in addresses])
    return list(out)
