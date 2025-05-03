
"""Utility to extract the first JSON object from a string fenced in a ```json code block."""
import json, re
from typing import Any, Dict

JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)

class JSONExtractError(ValueError):
    """Raised when JSON block cannot be found or parsed."""

def extract_json_block(text: str) -> Dict[str, Any]:
    """Return the JSON object contained in the first ```json fenced block.

    Raises
    ------
    JSONExtractError
        If no block found or JSON invalid.
    """
    m = JSON_BLOCK_RE.search(text)
    if not m:
        raise JSONExtractError("No JSON block found")
    block = m.group(1)
    try:
        return json.loads(block)
    except json.JSONDecodeError as e:
        raise JSONExtractError(f"Invalid JSON: {e}") from e
