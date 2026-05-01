"""Auto-withdrawal scheduler — runs every N days, checks unsettled balance,
logs a withdrawal-reminder notification (since the public Mystnodes API is read-only,
the actual withdrawal must be confirmed by the user on mystnodes.com).
"""
import asyncio
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from services.aggregator import get_snapshot

_scheduler: Optional[AsyncIOScheduler] = None
_db = None  # set by server on startup
_state: Dict[str, Any] = {
    "job_id": "auto-withdrawal",
    "next_run_at": None,
    "last_run_at": None,
}


def set_db(db) -> None:
    global _db
    _db = db


async def _run_withdrawal_check() -> Dict[str, Any]:
    """Compute unsettled balance, write a notification, update next_run."""
    snap = await get_snapshot(include_ai=False)
    derived = snap.get("derived", {})
    unsettled = float(derived.get("earnings_unsettled_myst", 0) or 0)
    threshold = float(os.environ.get("AUTO_WITHDRAWAL_THRESHOLD_MYST", 5))
    days = int(os.environ.get("AUTO_WITHDRAWAL_DAYS", 5))
    now = datetime.now(timezone.utc)
    triggered = unsettled >= threshold
    note = {
        "id": str(uuid.uuid4()),
        "created_at": now.isoformat(),
        "type": "withdrawal_reminder",
        "triggered": triggered,
        "unsettled_myst": unsettled,
        "threshold_myst": threshold,
        "settled_myst": float(derived.get("earnings_settled_myst", 0) or 0),
        "lifetime_myst": float(derived.get("earnings_lifetime_myst", 0) or 0),
        "myst_price_usd": float(derived.get("myst_price_usd", 0) or 0),
        "unsettled_usd": round(unsettled * float(derived.get("myst_price_usd", 0) or 0), 2),
        "action_url": "https://mystnodes.com",
        "message": (
            f"Unsettled balance {unsettled:.4f} MYST {'meets' if triggered else 'is below'} "
            f"threshold of {threshold} MYST. "
            + ("Visit mystnodes.com to confirm the withdrawal." if triggered else "No action needed.")
        ),
    }
    if _db is not None:
        try:
            await _db.withdrawal_logs.insert_one({**note, "_id": note["id"]})
        except Exception:
            pass
    _state["last_run_at"] = now.isoformat()
    _state["next_run_at"] = (now + timedelta(days=days)).isoformat()
    return note


def start(loop: asyncio.AbstractEventLoop) -> None:
    global _scheduler
    if _scheduler is not None:
        return
    days = int(os.environ.get("AUTO_WITHDRAWAL_DAYS", 5))
    _scheduler = AsyncIOScheduler(event_loop=loop, timezone="UTC")
    _scheduler.add_job(
        _run_withdrawal_check,
        IntervalTrigger(days=days),
        id=_state["job_id"],
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=3600,
    )
    _scheduler.start()
    job = _scheduler.get_job(_state["job_id"])
    if job and job.next_run_time:
        _state["next_run_at"] = job.next_run_time.astimezone(timezone.utc).isoformat()
    else:
        _state["next_run_at"] = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def shutdown() -> None:
    global _scheduler
    if _scheduler is not None:
        try:
            _scheduler.shutdown(wait=False)
        except Exception:
            pass
        _scheduler = None


async def trigger_now() -> Dict[str, Any]:
    return await _run_withdrawal_check()


def get_state() -> Dict[str, Any]:
    days = int(os.environ.get("AUTO_WITHDRAWAL_DAYS", 5))
    threshold = float(os.environ.get("AUTO_WITHDRAWAL_THRESHOLD_MYST", 5))
    next_run = _state["next_run_at"]
    if _scheduler is not None:
        job = _scheduler.get_job(_state["job_id"])
        if job and job.next_run_time:
            next_run = job.next_run_time.astimezone(timezone.utc).isoformat()
    return {
        "interval_days": days,
        "threshold_myst": threshold,
        "next_run_at": next_run,
        "last_run_at": _state["last_run_at"],
    }
