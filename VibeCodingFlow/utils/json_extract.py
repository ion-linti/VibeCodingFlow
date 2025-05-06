import json
import re
from typing import Any, Dict

class JSONExtractError(ValueError):
    """Raised when JSON block cannot be found or parsed."""

def extract_json_block(text: str) -> Dict[str, Any]:
    """Extract the first JSON object from a ```json fenced block.

    Args:
        text: Input string containing the JSON block.

    Returns:
        Parsed JSON object as a dictionary.

    Raises:
        JSONExtractError: If no JSON block is found or JSON is invalid.
    """
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        raise JSONExtractError("No JSON block found")
    
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise JSONExtractError(f"Invalid JSON: {e}") from e
