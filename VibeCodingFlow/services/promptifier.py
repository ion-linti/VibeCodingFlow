
import json
from typing import Dict

from ..utils.json_extract import extract_json_block, JSONExtractError
from .openai_client import chat
from ..prompts import PROMPT_PROMPTIFIER_USER, PROMPT_PROMPTIFIER_SYSTEM

async def build_spec(user_request: str) -> Dict:
    """Convert *user_request* into an initial structured project spec."""

    raw = await chat(
        PROMPT_PROMPTIFIER_USER.format(user_request=user_request),
        system=PROMPT_PROMPTIFIER_SYSTEM,
        temperature=0.3,
    )

    try:
        return extract_json_block(raw)
    except JSONExtractError as exc:
        raise ValueError(f"Promptifier step failed: {exc}. Full text: {raw!r}") from exc
