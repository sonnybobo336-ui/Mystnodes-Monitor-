"""Mystnodes (my.mystnodes.com) API client. Requires email/password.

Flow: POST /api/v2/auth/login -> accessToken (Bearer) -> use for /api/v2/node etc.
Endpoints reverse-engineered from github.com/Sch8ill/mystprom (Apache-2.0).
"""
import asyncio
import time
from typing import Any, Dict, List, Optional
import httpx

BASE = "https://my.mystnodes.com"
LOGIN_PATH = "/api/v2/auth/login"
REFRESH_PATH = "/api/v2/auth/refresh"
NODE_PATH = "/api/v2/node"
TOTALS_PATH = "/api/v1/metrics/node-totals"
ME_PATH = "/api/v2/me"


class MystnodesAuthError(Exception):
    pass


class MystnodesClient:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self._access_token: Optional[str] = None
        self._access_expires_at: float = 0.0
        self._refresh_token: Optional[str] = None
        self._refresh_expires_at: float = 0.0

    async def login(self) -> None:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"{BASE}{LOGIN_PATH}",
                json={"email": self.email, "password": self.password, "rememberMe": True},
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
            if r.status_code != 200:
                raise MystnodesAuthError(f"Mystnodes login failed: {r.status_code} {r.text[:200]}")
            data = r.json()
            self._access_token = data.get("accessToken")
            self._refresh_token = data.get("refreshToken")
            self._access_expires_at = time.time() + (data.get("accessTokenTTLMs", 600000) / 1000.0) - 30
            self._refresh_expires_at = time.time() + (data.get("refreshTokenTTLMs", 86400000) / 1000.0) - 30

    async def _refresh(self) -> None:
        if not self._refresh_token:
            return await self.login()
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"{BASE}{REFRESH_PATH}",
                json={"refreshToken": self._refresh_token},
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
            if r.status_code != 200:
                # Re-login
                return await self.login()
            data = r.json()
            self._access_token = data.get("accessToken")
            self._access_expires_at = time.time() + (data.get("accessTokenTTLMs", 600000) / 1000.0) - 30

    async def _ensure_auth(self) -> None:
        now = time.time()
        if not self._access_token or now >= self._access_expires_at:
            if self._refresh_token and now < self._refresh_expires_at:
                await self._refresh()
            else:
                await self.login()

    async def _get(self, path: str) -> Any:
        await self._ensure_auth()
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.get(
                f"{BASE}{path}",
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "Accept": "application/json",
                },
            )
            if r.status_code == 401:
                await self.login()
                r = await client.get(
                    f"{BASE}{path}",
                    headers={"Authorization": f"Bearer {self._access_token}", "Accept": "application/json"},
                )
            r.raise_for_status()
            return r.json()

    # Public methods
    async def list_nodes(self) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        page = 1
        while True:
            data = await self._get(f"{NODE_PATH}?page={page}&itemsPerPage=100")
            page_nodes = data.get("nodes", []) if isinstance(data, dict) else []
            nodes.extend(page_nodes)
            total = data.get("total", 0) if isinstance(data, dict) else 0
            if len(nodes) >= total or not page_nodes:
                break
            page += 1
        return nodes

    async def node(self, identity: str) -> Dict[str, Any]:
        return await self._get(f"{NODE_PATH}/{identity}")

    async def sessions(self, identity: str) -> List[Dict[str, Any]]:
        try:
            data = await self._get(f"{NODE_PATH}/{identity}/sessions")
            return data if isinstance(data, list) else []
        except Exception:
            return []

    async def totals(self, identities: List[str]) -> Dict[str, Any]:
        ids = ",".join(identities)
        return await self._get(f"{TOTALS_PATH}?days=30&identities={ids}")

    async def me(self) -> Dict[str, Any]:
        return await self._get(ME_PATH)


# Singleton holder
_client: Optional[MystnodesClient] = None


def configure(email: str, password: str) -> None:
    global _client
    _client = MystnodesClient(email=email, password=password)


def get_client() -> Optional[MystnodesClient]:
    return _client


async def test_credentials(email: str, password: str) -> Dict[str, Any]:
    """Quick credential check that returns user info on success."""
    c = MystnodesClient(email=email, password=password)
    try:
        await c.login()
        info = await c.me()
        return {"ok": True, "user": info}
    except Exception as e:
        return {"ok": False, "error": str(e)}
