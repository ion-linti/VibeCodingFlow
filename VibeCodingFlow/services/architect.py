
import json
from typing import Dict

from ..utils.json_extract import extract_json_block, JSONExtractError
from .openai_client import chat
from ..prompts import PROMPT_ARCHITECT_SYSTEM, PROMPT_ARCHITECT_USER

async def enrich_spec(spec: Dict) -> Dict:
    """Take *spec* produced by promptifier and add architecture details via LLM."""

    raw = await chat(
        PROMPT_ARCHITECT_USER.format(spec_json=json.dumps(spec, ensure_ascii=False, indent=2)),
        system=PROMPT_ARCHITECT_SYSTEM,
    )

    try:
        return extract_json_block(raw)
    except JSONExtractError as exc:
        raise ValueError(f"Architect step failed: {exc}. Full text: {raw!r}") from exc
