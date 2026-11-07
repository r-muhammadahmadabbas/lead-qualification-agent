"""LLM access with an offline-safe deterministic fallback."""
from __future__ import annotations

import logging
from typing import Any, Dict

from .config import LLM_MODEL, LLM_TEMPERATURE, OPENROUTER_API_KEY

logger = logging.getLogger(__name__)


def _fallback_draft(state: Dict[str, Any]) -> str:
    """Template used when no LLM key is configured or the provider fails."""
    company = state.get("company") or "your company"
    industry = (state.get("company_info") or {}).get("industry", "your industry")
    qualification = state.get("qualification", "unknown")
    return (
        f"Assalam-o-Alaikum {state.get('name', 'there')},\n\n"
        f"Thank you for reaching out to Web3Geeks about {company} ({industry}). "
        f"We reviewed your inquiry and classified it as a {qualification}-priority "
        f"opportunity. Our team will follow up within one business day with a "
        f"tailored scope, timeline and budget range.\n\n"
        f"If anything is urgent, simply reply to this email and we will prioritise it.\n\n"
        f"Best regards,\nWeb3Geeks Client Team"
    )


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call the configured LLM, or raise if unavailable."""
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    import litellm

    response = litellm.completion(
        model=LLM_MODEL,
        api_key=OPENROUTER_API_KEY,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=LLM_TEMPERATURE,
    )
    return response.choices[0].message.content


def draft_with_llm_or_fallback(state: Dict[str, Any]) -> str:
    """Draft a response, falling back to a deterministic template."""
    system_prompt = (
        "You are a sales assistant for Web3Geeks, a web3 development agency. "
        "Draft a professional, personalized response to a client inquiry. "
        "Be concise, friendly, and specific to their needs."
    )
    user_prompt = (
        "Client Inquiry:\n"
        f"Name: {state.get('name', '')}\n"
        f"Company: {state.get('company', 'N/A')}\n"
        f"Industry: {(state.get('company_info') or {}).get('industry', 'Unknown')}\n"
        f"Budget Range: {(state.get('company_info') or {}).get('budget_range', 'Unknown')}\n"
        f"Message: {state.get('message', '')}\n\n"
        "Draft a response."
    )
    try:
        return call_llm(system_prompt, user_prompt)
    except Exception as exc:  # noqa: BLE001 - provider failures must not break the flow
        logger.warning("LLM unavailable (%s); using deterministic draft", exc)
        return _fallback_draft(state)
