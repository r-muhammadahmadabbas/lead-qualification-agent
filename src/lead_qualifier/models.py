"""Pydantic request/response models."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class InquiryRequest(BaseModel):
    inquiry_id: str = Field(..., examples=["INQ-001"])
    name: str = Field(..., min_length=1)
    email: str
    company: str = ""
    message: str
    auto_approve: bool = Field(
        default=True,
        description="When false, low/medium leads stay in pending_review.",
    )


class InquiryResponse(BaseModel):
    inquiry_id: str
    status: str
    qualification: Optional[str] = None
    approved: Optional[bool] = None
    draft_response: Optional[str] = None
    latency: float = 0.0
    tool_calls: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
