"""Command-line interface for the lead-qualification agent."""
from __future__ import annotations

import argparse
import json

from .graph import run_inquiry

SAMPLE = {
    "inquiry_id": "INQ-001",
    "name": "John Smith",
    "email": "john@techcorp.com",
    "company": "TechCorp Solutions",
    "message": (
        "We need a web3 integration for our enterprise platform. Looking for "
        "smart contract development and DeFi features. Budget is flexible."
    ),
}


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="lead-qualifier")
    parser.add_argument("--inquiry", help="Path to a JSON file containing one inquiry")
    parser.add_argument("--sample", action="store_true", help="Run the bundled sample inquiry")
    args = parser.parse_args(argv)

    if args.inquiry:
        with open(args.inquiry, encoding="utf-8") as fh:
            payload = json.load(fh)
    else:
        payload = SAMPLE

    result = run_inquiry(payload)
    print(
        json.dumps(
            {
                "inquiry_id": result.get("inquiry_id"),
                "status": result.get("status"),
                "qualification": result.get("qualification"),
                "lead_score": result.get("lead_score"),
                "approved": result.get("approved"),
                "latency_seconds": round(result.get("latency", 0.0), 3),
                "tool_calls": result.get("tool_calls", []),
                "draft_response": result.get("draft_response"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
