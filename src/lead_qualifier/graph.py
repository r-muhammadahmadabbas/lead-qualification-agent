"""LangGraph wiring for the client-inquiry qualification workflow."""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from .nodes import (
    draft_response,
    handle_error,
    human_review,
    qualify_lead,
    research_company,
    route_after_qualification,
    route_after_validation,
    validate_input,
)
from .state import InquiryState, initial_state

WORKFLOW_DIAGRAM = """
validate ──► research ──► qualify ──► draft ──► human_review ──► END
    │                        │
    └──► error_handler ◄─────┘ ──► END
"""


def build_graph():
    workflow = StateGraph(InquiryState)

    workflow.add_node("validate", validate_input)
    workflow.add_node("research", research_company)
    workflow.add_node("qualify", qualify_lead)
    workflow.add_node("draft", draft_response)
    workflow.add_node("human_review", human_review)
    workflow.add_node("error_handler", handle_error)

    workflow.set_entry_point("validate")
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {"research": "research", "error_handler": "error_handler"},
    )
    workflow.add_edge("research", "qualify")
    workflow.add_conditional_edges(
        "qualify",
        route_after_qualification,
        {"draft": "draft", "error_handler": "error_handler"},
    )
    workflow.add_edge("draft", "human_review")
    workflow.add_edge("human_review", END)
    workflow.add_edge("error_handler", END)
    return workflow.compile()


@lru_cache(maxsize=1)
def get_graph():
    """Compile the graph once per process."""
    return build_graph()


def run_inquiry(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single inquiry through the agent graph."""
    state = initial_state(payload)
    return get_graph().invoke(state)
