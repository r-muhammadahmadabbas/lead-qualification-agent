# Lead Qualification Agent

[![CI](https://github.com/your-org/lead-qualification-agent/actions/workflows/ci.yml/badge.svg)](../../actions)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A stateful **LangGraph** agent that receives inbound client inquiries, validates them, researches the company, scores the lead, drafts a personalized reply, and pauses at a human‑in‑the‑loop approval gate. Built for **Web3Geeks**, a web3 development agency, but the workflow is reusable for any B2B service business.

The agent is **offline‑safe**: without an LLM key it still runs end‑to‑end using a deterministic draft template, so CI and local development never depend on a paid provider.

---

## Workflow

```text
                 ┌────────────────┐
   inquiry ─────►│   validate   │
                 └──────┬───────┘
             invalid    │ valid
        ┌───────────────┴────────────────┐
        ▼                                ▼
  ┌──────────────┐                 ┌────────────────┐
  │ error_handler│                 │   research   │
  └──────┬───────┘                 └──────┬───────┘
        │                                ▼
        │                         ┌────────────────┐
        │                         │   qualify    │
        │                         └──────┬───────┘
        │                low             │ medium / high
        │        ┌───────────────────────┴────────────┐
        │        ▼                                    ▼
        │ ┌──────────────┐                     ┌────────────────┐
        └►│ error_handler│                     │    draft     │
          └──────────────┘                     └──────┬───────┘
                                                    ▼
                                            ┌────────────────┐
                                            │ human_review │
                                            └──────┬───────┘
                                                   ▼
                                                  END
```

| Node | Responsibility |
| --- | --- |
| `validate` | Name length, email format, message length |
| `research` | Match company against the local CRM database |
| `qualify` | Rule‑based score → `high` / `medium` / `low` |
| `draft` | LLM response, or deterministic template fallback |
| `human_review` | Auto‑approve or park in `pending_review` |
| `error_handler` | Safe, user‑facing failure response |

| Signal | Points |
| --- | --- |
| Company budget: high / medium / low | +3 / +2 / +1 |
| Urgency words (`urgent`, `asap`, `immediately`) | +2 |
| Budget words (`budget`, `price`, `cost`, `quote`) | +1 |
| Domain words (`web3`, `blockchain`, `defi`, `nft`, …) | +2 |

- `>= 5` → **high** (auto‑approved)
- `>= 3` → **medium** (auto‑approved)
- `< 3` → **low** → routed to the safe error handler

Set `auto_approve=false` on a request to force every lead into `pending_review` for a human decision.

---

## Project Structure

```text
lead-qualification-agent/
├── .github/workflows/ci.yml              # GitHub Actions CI
├── .env.example                         # OpenRouter API key (optional)
├── data/companies.json                   # Local CRM snapshot
├── docs/                                 # Architecture, monitoring, evaluation notes
├── scripts/run_evaluation.py             # 8‑case evaluation suite
├── src/lead_qualifier/
│   ├── config.py                        # Env‑driven configuration
│   ├── state.py                         # TypedDict graph state
│   ├── tools.py                         # Company lookup, validation, scoring
│   ├── llm.py                           # Provider call + offline fallback
│   ├── nodes.py                         # Graph nodes and routing
│   ├── graph.py                         # StateGraph wiring
│   ├── models.py                        # Pydantic API contracts
│   ├── api.py                           # FastAPI service
│   └── cli.py                           # Local runner
└── tests/                               # Offline unit + graph tests
```

---

## Quick Start

```bash
git clone https://github.com/your-org/lead-qualification-agent.git
cd lead-qualification-agent

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # macOS / Linux

pip install -e ".[dev]"
cp .env.example .env              # optional: add OPENROUTER_API_KEY

pytest                            # run the offline test suite
python -m lead_qualifier.cli --sample   # run the bundled sample inquiry
```

### Example Output

```json
{
  "inquiry_id": "INQ-001",
  "status": "approved",
  "qualification": "high",
  "lead_score": 8,
  "approved": true,
  "latency_seconds": 0.001,
  "tool_calls": [
    "validate_input:PASS",
    "research_company:FOUND:TechCorp Solutions",
    "qualify_lead:high:8",
    "draft_response"
  ],
  "draft_response": "Assalam-o-Alaikum John Smith, ..."
}
```

### API

```bash
uvicorn lead_qualifier.api:app --reload
```

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness probe |
| `GET` | `/workflow` | ASCII workflow diagram |
| `POST` | `/qualify` | Run an inquiry through the graph |

```bash
curl -X POST http://localhost:8000/qualify \
  -H "Content-Type: application/json" \
  -d '{"inquiry_id":"INQ-001","name":"John Smith","email":"john@techcorp.com","company":"TechCorp Solutions","message":"We need a web3 integration with smart contracts. Budget is flexible."}'
```

Interactive docs: <http://localhost:8000/docs>

---

## Evaluation

```bash
python scripts/run_evaluation.py
```

The suite covers normal enterprise/startup/agency inquiries, empty input, invalid email, unknown companies, SQL‑injection strings, and oversized messages. Every case returns a structured result and a tool‑call trace instead of crashing.

---

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | empty | Enables real LLM drafting |
| `LLM_MODEL` | `openrouter/meta-llama/llama-3.3-70b-instruct` | Model identifier |
| `LLM_TEMPERATURE` | `0.3` | Sampling temperature |
| `HIGH_QUALIFICATION_SCORE` | `5` | High‑lead cutoff |
| `MEDIUM_QUALIFICATION_SCORE` | `3` | Medium‑lead cutoff |
| `COMPANIES_PATH` | `data/companies.json` | CRM snapshot |
| `LOG_DIR` | `logs/` | Structured log destination |

---

## Testing

```bash
pytest -q
ruff check src tests
```

Tests are hermetic: they do not call an LLM and do not require network access.

---

## Docker

```bash
docker compose up --build
```

The API is exposed on `http://localhost:8000`.

---

## Design Notes

- **Deterministic core, LLM at the edge.** Validation, research and scoring are plain Python, so they are cheap, testable and reproducible. The LLM only writes the customer‑facing draft.
- **Graceful degradation.** A missing/broken provider key never blocks the workflow.
- **Human‑in‑the‑loop by default in production.** Set `auto_approve=false` when replies must be reviewed before sending.
- **Full observability.** Every node appends to `tool_calls`, and latency is accumulated in state and returned by the API.

---

## License

MIT