import json
from .openai_client import chat
from ..prompts import PROMPT_PROMPTIFIER_USER, PROMPT_PROMPTIFIER_SYSTEM

async def build_spec(user_request: str) -> dict:
    raw = await chat(
        PROMPT_PROMPTIFIER_USER.format(user_request=user_request),
        system=PROMPT_PROMPTIFIER_SYSTEM,
        temperature=0.3
    )
    start = raw.find('{')
    if start == -1:
        raise ValueError(f'No JSON object found: {raw!r}')
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
