"""Tailscale API client (read-only device list)."""
from typing import Any, Dict, List, Optional
import httpx

BASE = "https://api.tailscale.com"


class TailscaleAuthError(Exception):
    pass


async def list_devices(api_key: str, tailnet: str = "-") -> List[Dict[str, Any]]:
    if not api_key:
        raise TailscaleAuthError("Missing Tailscale API key")
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    url = f"{BASE}/api/v2/tailnet/{tailnet}/devices"
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        r = await client.get(url)
        if r.status_code != 200:
            r2 = await client.get(url, auth=(api_key, ""))
            if r2.status_code == 200:
                r = r2
            else:
                raise TailscaleAuthError(f"Tailscale {r.status_code}: {r.text[:300]}")
        data = r.json()
    return data.get("devices", [])


async def test_credentials(api_key: str, tailnet: str = "-") -> Dict[str, Any]:
    try:
        devices = await list_devices(api_key, tailnet)
        return {"ok": True, "count": len(devices)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
