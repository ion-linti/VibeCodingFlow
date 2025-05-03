
"""Thin async wrapper around OpenAI ChatCompletion.

* Requires ``OPENAI_API_KEY`` env var.
* Model can be overridden with ``VIBE_MODEL`` env var.
* Provides basic retry / timeout.
"""
import os
import asyncio
from typing import Optional, List, Dict
from openai import AsyncOpenAI, OpenAIError

_API_KEY = os.getenv("OPENAI_API_KEY")
if not _API_KEY:
    raise RuntimeError(
        "⚠️  Environment variable OPENAI_API_KEY is not set. "
        "Export your key first, e.g. `export OPENAI_API_KEY=sk-...`"
    )

_DEFAULT_MODEL = os.getenv("VIBE_MODEL", "gpt-4o")
_MAX_RETRIES = 3
_TIMEOUT = 60  # seconds

_client = AsyncOpenAI(
    api_key=_API_KEY,
    max_retries=_MAX_RETRIES,
    timeout=_TIMEOUT,
)

async def chat(
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    """Send a single-turn chat prompt and return **content** of first assistant message."""

    mdl = model or _DEFAULT_MODEL
    messages: List[Dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = await _client.chat.completions.create(
            model=mdl,
            messages=messages,
            temperature=temperature,
        )
    except OpenAIError as exc:
        # Re‑raise with nicer message so CLI prints pretty error
        raise RuntimeError(f"OpenAI API error: {exc}") from exc

    return response.choices[0].message.content.strip()
