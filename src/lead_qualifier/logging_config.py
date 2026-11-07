"""Logging configuration."""
from __future__ import annotations

import logging
import sys

from .config import LOG_DIR


def configure_logging(level: str = "INFO") -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_DIR / "agent.log", encoding="utf-8"),
        ],
        force=True,
    )
