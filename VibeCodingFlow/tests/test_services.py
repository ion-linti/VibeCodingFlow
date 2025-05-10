
from __future__ import annotations

import pytest

from VibeCodingFlow.services.architect import enrich_spec
from VibeCodingFlow.services import architect as architect_module
from VibeCodingFlow.services.updater import diff_specs


class _DummyChat:
    """Simple stub for openai_client.chat returning a JSON object wrapped in noise."""

    async def __call__(
        self,
        prompt: str,
        system: str | None = None,
        model: str = "gpt-4o",
        temperature: float = 0.2,
    ) -> str:  # noqa: D401
        return (
            "Sure thing, here is the enriched spec:\n"
            "{\n  \"key\": \"value\"\n}\n"
            "Hope that helps!"
        )


@pytest.mark.asyncio
async def test_enrich_spec_extracts_json(monkeypatch):
    """``enrich_spec`` should parse the first balanced JSON object from the LLM response."""

    # Replace the real chat function with the stub.
    monkeypatch.setattr(architect_module, "chat", _DummyChat())
    spec_in = {"name": "demo"}

    spec_out = await enrich_spec(spec_in)

    assert spec_out == {"key": "value"}


def test_diff_specs_detects_new_files():
    """``diff_specs`` should list any files that are new or whose description changes."""

    old = {"project_structure": {"a.py": "desc A"}}
    new = {"project_structure": {"a.py": "desc A", "b.py": "desc B"}}

    assert diff_specs(old, new) == ["b.py"]
