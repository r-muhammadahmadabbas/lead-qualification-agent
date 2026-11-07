"""LangGraph state definition."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class InquiryState(TypedDict, total=False):
    inquiry_id: str
    name: str
    email: str
    company: str
    message: str
    auto_approve: bool

    company_info: Dict[str, Any]
    qualification: str
    lead_score: int
    draft_response: str
    approved: bool

    status: str
    error: str
    tool_calls: List[str]
    latency: float
    token_count: int


def initial_state(payload: Dict[str, Any]) -> InquiryState:
    """Normalise arbitrary input into a complete initial graph state."""
    return {
        "inquiry_id": payload.get("inquiry_id", ""),
        "name": payload.get("name", ""),
        "email": payload.get("email", ""),
        "company": payload.get("company", ""),
        "message": payload.get("message", ""),
        "auto_approve": bool(payload.get("auto_approve", True)),
        "company_info": {},
        "qualification": "",
        "lead_score": 0,
        "draft_response": "",
        "approved": False,
        "status": "new",
        "error": "",
        "tool_calls": [],
        "latency": 0.0,
        "token_count": 0,
    }
