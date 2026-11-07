from lead_qualifier.graph import run_inquiry
from lead_qualifier.tools import (
    qualification_from_score,
    score_lead,
    search_company,
    validate_email,
)


def test_validate_email_accepts_and_rejects():
    assert validate_email("john@techcorp.com")
    assert not validate_email("not-an-email")
    assert not validate_email("")


def test_search_company_is_case_insensitive():
    company = search_company("techcorp")
    assert company is not None
    assert company["budget_range"] == "high"
    assert search_company("does-not-exist") is None


def test_score_lead_rewards_high_budget_and_domain_intent():
    score = score_lead(
        "We need urgent smart contract development, budget flexible",
        {"budget_range": "high"},
    )
    assert score >= 7
    assert qualification_from_score(score) == "high"


def test_low_signal_message_is_low_quality():
    score = score_lead("hello", {"budget_range": "low"})
    assert score < 3
    assert qualification_from_score(score) == "low"


def _payload(**overrides):
    base = {
        "inquiry_id": "TC-001",
        "name": "John Smith",
        "email": "john@techcorp.com",
        "company": "TechCorp Solutions",
        "message": "We need a web3 integration for our enterprise platform with blockchain features.",
    }
    base.update(overrides)
    return base


def test_graph_approves_high_quality_lead():
    result = run_inquiry(_payload())
    assert result["status"] == "approved"
    assert result["qualification"] == "high"
    assert result["approved"] is True
    assert result["draft_response"]
    assert result["latency"] >= 0


def test_graph_marks_invalid_email_as_error():
    result = run_inquiry(_payload(email="not-an-email"))
    assert result["status"] == "error"
    assert "email" in result["error"].lower()


def test_graph_keeps_low_quality_lead_out_of_approval():
    result = run_inquiry(_payload(message="hello there", company="SmallBiz Local"))
    assert result["status"] == "error"
    assert result["approved"] is False


def test_auto_approve_false_pends_high_quality_lead():
    result = run_inquiry(_payload(auto_approve=False))
    assert result["status"] == "pending_review"
    assert result["approved"] is False
