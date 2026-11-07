"""Configuration for the lead-qualification agent."""
from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parents[1]

DATA_DIR = PROJECT_ROOT / "data"
COMPANIES_PATH = Path(os.getenv("COMPANIES_PATH", DATA_DIR / "companies.json"))
LOG_DIR = Path(os.getenv("LOG_DIR", PROJECT_ROOT / "logs"))

# LLM provider (OpenRouter via litellm). The agent degrades gracefully to a
# deterministic draft when no key is configured.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
LLM_MODEL = os.getenv(
    "LLM_MODEL", "openrouter/meta-llama/llama-3.3-70b-instruct"
)
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# Lead-scoring thresholds
HIGH_QUALIFICATION_SCORE = int(os.getenv("HIGH_QUALIFICATION_SCORE", "5"))
MEDIUM_QUALIFICATION_SCORE = int(os.getenv("MEDIUM_QUALIFICATION_SCORE", "3"))

MIN_NAME_LENGTH = 2
MIN_MESSAGE_LENGTH = 10
