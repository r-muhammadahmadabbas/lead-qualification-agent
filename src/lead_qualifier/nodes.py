"""LangGraph nodes and routing functions."""
from __future__ import annotations

import logging
import time

from .config import MIN_MESSAGE_LENGTH, MIN_NAME_LENGTH
from .llm import draft_with_llm_or_fallback
from .state import InquiryState
from .tools import (
    qualification_from_score,
    score_lead,
    search_company,
    validate_email,
)

logger = logging.getLogger(__name__)


def validate_input(state: InquiryState) -> InquiryState:
    start = time.perf_counter()
    errors = []

    if not state.get("name") or len(state["name"].strip()) < MIN_NAME_LENGTH:
        errors.append(f"Name must be at least {MIN_NAME_LENGTH} characters")
    if not state.get("email") or not validate_email(state["email"]):
        errors.append("Invalid email format")
    if not state.get("message") or len(state["message"].strip()) < MIN_MESSAGE_LENGTH:
        errors.append(f"Message must be at least {MIN_MESSAGE_LENGTH} characters")

    latency = time.perf_counter() - start
    tool_calls = state.get("tool_calls", []) + [
        "validate_input:FAIL" if errors else "validate_input:PASS"
    ]

    if errors:
        return {
            **state,
            "status": "error",
            "error": "; ".join(errors),
            "latency": state.get("latency", 0.0) + latency,
            "tool_calls": tool_calls,
        }

    return {
        **state,
        "status": "valid",
        "error": "",
        "latency": state.get("latency", 0.0) + latency,
        "tool_calls": tool_calls,
    }


def research_company(state: InquiryState) -> InquiryState:
    start = time.perf_counter()
    company_name = state.get("company", "")

    if not company_name:
        info = {"name": "Unknown", "industry": "Unknown", "budget_range": "unknown"}
        tag = "research_company:NO_COMPANY"
    else:
        info = search_company(company_name)
        tag = (
            f"research_company:FOUND:{company_name}"
            if info
            else f"research_company:NOT_FOUND:{company_name}"
        )
        info = info or {
            "name": company_name,
            "industry": "Unknown",
            "budget_range": "unknown",
        }

    return {
        **state,
        "company_info": info,
        "tool_calls": state.get("tool_calls", []) + [tag],
        "latency": state.get("latency", 0.0) + (time.perf_counter() - start),
    }


def qualify_lead(state: InquiryState) -> InquiryState:
    start = time.perf_counter()
    score = score_lead(state.get("message", ""), state.get("company_info", {}))
    qualification = qualification_from_score(score)

    return {
        **state,
        "qualification": qualification,
        "lead_score": score,
        "tool_calls": state.get("tool_calls", [])
        + [f"qualify_lead:{qualification}:{score}"],
        "latency": state.get("latency", 0.0) + (time.perf_counter() - start),
    }


def draft_response(state: InquiryState) -> InquiryState:
    start = time.perf_counter()
    text = draft_with_llm_or_fallback(state)
    return {
        **state,
        "draft_response": text,
        "token_count": len(text.split()),
        "tool_calls": state.get("tool_calls", []) + ["draft_response"],
        "latency": state.get("latency", 0.0) + (time.perf_counter() - start),
    }


def human_review(state: InquiryState) -> InquiryState:
    """Human-in-the-loop checkpoint.

    High and medium leads are auto-approved when ``auto_approve`` is true;
    otherwise they remain in ``pending_review`` for a human.
    """
    qualification = state.get("qualification")
    auto_approve = state.get("auto_approve", True)

    if qualification in {"high", "medium"} and auto_approve:
        return {**state, "approved": True, "status": "approved"}

    return {
        **state,
        "approved": False,
        "status": "pending_review" if qualification in {"high", "medium"} else "rejected",
    }


def handle_error(state: InquiryState) -> InquiryState:
    logger.warning("Handling inquiry error: %s", state.get("error", "unknown"))
    return {
        **state,
        "status": "error",
        "draft_response": (
            f"We encountered an issue: {state.get('error', 'Unknown error')}. "
            "Please try again."
        ),
        "tool_calls": state.get("tool_calls", []) + ["handle_error"],
    }


def route_after_validation(state: InquiryState) -> str:
    return "error_handler" if state.get("status") == "error" else "research"


def route_after_qualification(state: InquiryState) -> str:
    return "error_handler" if state.get("qualification") == "low" else "draft"
