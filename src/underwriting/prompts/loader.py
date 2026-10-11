"""Load a versioned prompt file from this package."""

from pathlib import Path


def load_prompt(filename: str) -> str:
    """Return the text of a prompt file stored next to this module."""
    path = Path(__file__).parent / filename
    return path.read_text(encoding="utf-8")
