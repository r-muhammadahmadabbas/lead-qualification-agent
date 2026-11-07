# Architecture

## Goals

1. Validate and qualify inbound B2B inquiries deterministically.
2. Only spend LLM tokens on the customer-facing draft.
3. Never let a provider outage break the workflow.
4. Keep a human approval gate for anything that will be sent to a client.

## Components

| Layer | Module | Notes |
| --- | --- | --- |
| State contract | `state.py` | `TypedDict` shared by every node |
| Deterministic tools | `tools.py` | Company lookup, email validation, scoring |
| LLM adapter | `llm.py` | litellm + offline fallback |
| Graph nodes | `nodes.py` | Pure functions `state -> state` (plus routing) |
| Orchestration | `graph.py` | `StateGraph`, conditional edges, compiled once |
| Transport | `api.py` | FastAPI + Pydantic models |
| Ops | `logging_config.py` | stdout + rotating file logs |

## Why the graph is structured this way

- **Validation first** keeps bad data out of every downstream node.
- **Research is separate from scoring** so the CRM lookup can be swapped for a
  web-search tool without touching the scoring policy.
- **Qualification is a conditional edge** rather than an `if` inside a god-node,
  which makes the routing visible in the graph diagram and easy to test.
- **Human review is a node**, so future versions can replace the auto-approval
  policy with a real queue without changing the graph shape.

## Failure policy

| Failure | Behaviour |
| --- | --- |
| Missing/invalid input | `error_handler` with a readable message |
| Unknown company | Research returns `Unknown` and qualification continues |
| Low score | Routed to `error_handler` (no reply drafted) |
| LLM error / no key | Deterministic template draft |
| Unexpected exception | API returns HTTP 500 and logs the trace |

## Extending the agent

1. Add a node function in `nodes.py` with signature `(state) -> state`.
2. Register it in `graph.py` with `workflow.add_node`.
3. Add a conditional edge if the node changes routing.
4. Add a unit test that invokes `run_inquiry()` and asserts on the state.
