"""Backend configuration and path settings for Chain Guard AI."""

import os
from pathlib import Path

# Filesystem layout
BACKEND_DIR = Path(__file__).resolve().parent
SRC_DIR = BACKEND_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = BACKEND_DIR / "data"

# Server parameters
SERVER_HOST: str = os.getenv("HOST", "0.0.0.0")
SERVER_PORT: int = int(os.getenv("PORT", 8000))
DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

# Standard regulatory cold-chain thermal thresholds (WHO/FDA GDP standard)
DEFAULT_VACCINE_MIN_TEMP_C: float = float(os.getenv("VACCINE_MIN_TEMP_C", 2.0))
DEFAULT_VACCINE_MAX_TEMP_C: float = float(os.getenv("VACCINE_MAX_TEMP_C", 8.0))
DEFAULT_EXCURSION_TOLERANCE_MINUTES: int = int(os.getenv("EXCURSION_TOLERANCE_MINUTES", 30))
