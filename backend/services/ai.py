"""AI insights via Emergent LLM key (Claude Sonnet 4.5)."""
import json
import os
import re
import uuid
from typing import Any, Dict
from emergentintegrations.llm.chat import LlmChat, UserMessage

MODEL_PROVIDER = "anthropic"
MODEL_NAME = "claude-sonnet-4-5-20250929"

SYSTEM_PROMPT = (
    "You are NodeForge AI, an analyst for cryptocurrency node operations (focus: Mysterium dVPN nodes). "
    "Given a JSON snapshot of prices, node metrics, sessions, earnings, wallet balances, and connectivity, "
    "return STRICT JSON ONLY with this schema:\n"
    '{\n'
    '  "underperformers": [{"id": str, "reason": str, "severity": "low"|"medium"|"high"}],\n'
    '  "revenue_loss_estimate_usd": number,\n'
    '  "recommendations": [str],\n'
    '  "summary": str\n'
    '}\n'
    "Rules: at most 4 underperformers, at most 6 recommendations, summary <= 240 chars. "
    "Each underperformer.reason <= 180 chars. No markdown, no prose, JSON only."
)


async def generate_insights(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        return {"error": "EMERGENT_LLM_KEY not configured"}
    chat = LlmChat(
        api_key=api_key,
        session_id=f"nodeforge-{uuid.uuid4()}",
        system_message=SYSTEM_PROMPT,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)
    compact = json.dumps(snapshot, default=str)[:6000]
    raw = await chat.send_message(UserMessage(text=f"Snapshot:\n{compact}\n\nReturn JSON only."))
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        return {"summary": text[:400], "underperformers": [], "recommendations": [], "revenue_loss_estimate_usd": 0, "_warning": "non-JSON model output"}
