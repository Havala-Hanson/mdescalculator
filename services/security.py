# services/security.py

import html
import re
import logging
from logging.handlers import RotatingFileHandler

# ------------------------------------------------------------
# Logging setup (rotating log, max 1MB, keep 3 backups)
# ------------------------------------------------------------
logger = logging.getLogger("security")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "security.log",
    maxBytes=1_000_000,
    backupCount=3,
    encoding="utf-8"
)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)

# ------------------------------------------------------------
# Security constraints
# ------------------------------------------------------------
MAX_INPUT_CHARS = 2000
MAX_LINES = 20
CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


class SecurityError(Exception):
    """Raised when user input violates security constraints."""
    pass


def sanitize_text(text: str) -> str:
    """
    Clean and validate user-provided text before passing it to the classifier.
    Logs violations for monitoring bot or abuse attempts.
    """

    if text is None:
        logger.warning("Rejected input: None provided")
        raise SecurityError("No text provided.")

    cleaned = text.strip()

    # Length limit
    if len(cleaned) > MAX_INPUT_CHARS:
        logger.warning(f"Rejected input: too long ({len(cleaned)} chars)")
        raise SecurityError(
            f"Input is too long ({len(cleaned)} characters). "
            f"Please shorten it to under {MAX_INPUT_CHARS} characters."
        )

    # Line count limit
    if cleaned.count("\n") > MAX_LINES:
        logger.warning("Rejected input: too many lines")
        raise SecurityError(
            "Input contains too many lines. "
            "Please provide a concise study description."
        )

    # Control characters
    if CONTROL_CHAR_PATTERN.search(cleaned):
        logger.warning("Rejected input: control characters detected")
        raise SecurityError(
            "Input contains unsupported control characters."
        )

    # Escape HTML
    cleaned = html.escape(cleaned)

    return cleaned