import json
from .openai_client import chat
from ..prompts import PROMPT_ARCHITECT_SYSTEM, PROMPT_ARCHITECT_USER

async def enrich_spec(spec: dict) -> dict:
    raw = await chat(
        PROMPT_ARCHITECT_USER.format(spec_json=json.dumps(spec, ensure_ascii=False, indent=2)),
        system=PROMPT_ARCHITECT_SYSTEM
    )
    start = raw.find('{')
    brace_count = 0
    end = None
    for idx, ch in enumerate(raw[start:], start):
        if ch == '{':
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0:
                end = idx + 1
                break
    if end is None:
        raise ValueError(f'Unmatched braces: {raw!r}')
    return json.loads(raw[start:end])
