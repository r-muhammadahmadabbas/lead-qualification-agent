"""Deterministic tools: company lookup, validation and lead scoring."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .config import (
    COMPANIES_PATH,
    HIGH_QUALIFICATION_SCORE,
    MEDIUM_QUALIFICATION_SCORE,
)

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

URGENCY_WORDS = ("urgent", "asap", "immediately")
BUDGET_WORDS = ("budget", "price", "cost", "quote")
DOMAIN_WORDS = ("web3", "blockchain", "smart contract", "defi", "nft")


def load_companies(path: Path = COMPANIES_PATH) -> list[Dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as fh:
        return json.load(fh)["companies"]


def search_company(company_name: str, path: Path = COMPANIES_PATH) -> Optional[Dict[str, Any]]:
    """Case-insensitive substring match against the local company database."""
    if not company_name:
        return None
    needle = company_name.lower().strip()
    for company in load_companies(path):
        name = company["name"].lower()
        if needle in name or name in needle:
            return company
    return None


def validate_email(email: str) -> bool:
    return bool(email and EMAIL_RE.match(email))


def score_lead(message: str, company_info: Optional[Dict[str, Any]] = None) -> int:
    """Rule-based lead score used by the qualification node."""
    company_info = company_info or {}
    message_lower = (message or "").lower()
    score = 0

    budget = company_info.get("budget_range", "unknown")
    score += {"high": 3, "medium": 2, "low": 1}.get(budget, 0)

    if any(word in message_lower for word in URGENCY_WORDS):
        score += 2
    if any(word in message_lower for word in BUDGET_WORDS):
        score += 1
    if any(word in message_lower for word in DOMAIN_WORDS):
        score += 2

    return score


def qualification_from_score(score: int) -> str:
    if score >= HIGH_QUALIFICATION_SCORE:
        return "high"
    if score >= MEDIUM_QUALIFICATION_SCORE:
        return "medium"
    return "low"


def timed(fn, *args, **kwargs):
    """Small helper that returns ``(result, elapsed_seconds)``."""
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, time.perf_counter() - start
