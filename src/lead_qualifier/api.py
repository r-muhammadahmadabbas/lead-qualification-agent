"""FastAPI service exposing the qualification agent."""
from __future__ import annotations

import logging
import time

from fastapi import FastAPI, HTTPException

from .graph import WORKFLOW_DIAGRAM, run_inquiry
from .models import HealthResponse, InquiryRequest, InquiryResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Web3Geeks Lead Qualification API",
    description="Qualify inbound client inquiries with a LangGraph agent.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="healthy", service="lead-qualification-agent", version="1.0.0")


@app.get("/workflow")
async def workflow() -> dict:
    return {"diagram": WORKFLOW_DIAGRAM}


@app.post("/qualify", response_model=InquiryResponse)
async def qualify(request: InquiryRequest) -> InquiryResponse:
    start = time.perf_counter()
    try:
        result = run_inquiry(request.model_dump())
    except Exception as exc:  # noqa: BLE001
        logger.exception("Inquiry failed: %s", request.inquiry_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return InquiryResponse(
        inquiry_id=result.get("inquiry_id", request.inquiry_id),
        status=result.get("status", "error"),
        qualification=result.get("qualification") or None,
        approved=result.get("approved"),
        draft_response=result.get("draft_response"),
        latency=round(time.perf_counter() - start, 4),
        tool_calls=result.get("tool_calls", []),
        error=result.get("error") or None,
    )
