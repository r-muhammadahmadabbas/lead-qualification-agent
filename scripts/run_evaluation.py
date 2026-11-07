"""Run the eight-case evaluation suite against the agent."""
from __future__ import annotations

import json
import time

from lead_qualifier.graph import run_inquiry

CASES = [
    ("Normal - Enterprise Client", {
        "inquiry_id": "TC-001", "name": "John Smith", "email": "john@techcorp.com",
        "company": "TechCorp Solutions",
        "message": "We need a web3 integration for our enterprise platform. Looking for smart contract development and DeFi features. Budget is flexible.",
    }),
    ("Normal - Startup Client", {
        "inquiry_id": "TC-002", "name": "Alice Johnson", "email": "alice@startupxyz.com",
        "company": "StartupXYZ",
        "message": "We're building a DeFi platform and need smart contract development. Our budget is around $20k.",
    }),
    ("Normal - Marketing Agency", {
        "inquiry_id": "TC-003", "name": "Sarah Williams", "email": "sarah@creativeagency.com",
        "company": "Creative Agency Co",
        "message": "We need NFT marketing services for our clients. Can you help us create NFT collections?",
    }),
    ("Edge - Empty Message", {
        "inquiry_id": "TC-004", "name": "Bob Test", "email": "bob@test.com",
        "company": "Test Corp", "message": "",
    }),
    ("Edge - Invalid Email", {
        "inquiry_id": "TC-005", "name": "Carol Test", "email": "not-an-email",
        "company": "Test Corp",
        "message": "This is a test message that should fail validation due to invalid email.",
    }),
    ("Edge - Unknown Company", {
        "inquiry_id": "TC-006", "name": "David Unknown", "email": "david@unknown.com",
        "company": "Unknown Company XYZ",
        "message": "We need blockchain consulting for our new project. What are your rates?",
    }),
    ("Adversarial - SQL Injection", {
        "inquiry_id": "TC-007", "name": "'; DROP TABLE users; --", "email": "hacker@evil.com",
        "company": "Evil Corp", "message": "SELECT * FROM users WHERE 1=1 OR 1=1 --",
    }),
    ("Adversarial - Very Long Message", {
        "inquiry_id": "TC-008", "name": "Long Writer", "email": "long@writer.com",
        "company": "Writer Corp", "message": "This is a very long message. " * 100,
    }),
]


def main() -> None:
    rows = []
    for name, inquiry in CASES:
        start = time.perf_counter()
        result = run_inquiry(inquiry)
        elapsed = time.perf_counter() - start
        rows.append({
            "test": name,
            "status": result.get("status"),
            "qualification": result.get("qualification", "N/A"),
            "score": result.get("lead_score", 0),
            "latency_s": round(elapsed, 3),
            "tool_calls": len(result.get("tool_calls", [])),
        })

    print(json.dumps(rows, indent=2))
    passed = sum(1 for r in rows if r["status"] in {"approved", "pending_review", "error"})
    print(f"\nProcessed {passed}/{len(rows)} cases without crashing.")


if __name__ == "__main__":
    main()
