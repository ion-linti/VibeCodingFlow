
import json
from pathlib import Path
from typing import Dict

from ..utils.json_extract import extract_json_block, JSONExtractError
from .openai_client import chat
from ..prompts import PROMPT_CODEGEN_PROJECT_SYSTEM, PROMPT_CODEGEN_PROJECT_USER


PROJECT_ROOT = Path('.')

def _safe_join(root: Path, rel: str) -> Path:
    """Return an absolute path inside *root* for the given relative path.

    Raises
    ------
    ValueError
        If *rel* tries to escape *root* using ``..`` components.
    """
    p = (root / rel.lstrip('/\\')).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError(f"Path traversal detected: {rel!r}")
    return p

async def generate_project(spec_full: Dict) -> None:
    """Generate full project files as described by *spec_full*."""

    # Ask LLM for mapping {filepath: code}
    raw = await chat(
        PROMPT_CODEGEN_PROJECT_USER.format(
            project_spec=json.dumps(spec_full.get('project_structure', {}), ensure_ascii=False)
        ),
        system=PROMPT_CODEGEN_PROJECT_SYSTEM,
        model='gpt-4o',
        temperature=0.4,
    )

    try:
        files = extract_json_block(raw)
    except JSONExtractError as exc:
        raise ValueError(f"LLM did not return a valid JSON mapping: {exc}. Full text: {raw!r}") from exc

    for rel_path, src in files.items():
        if not rel_path or rel_path in ('/', '.', '') or rel_path.endswith('/'):
            # Skip empty or directory entries
            continue

        path = _safe_join(PROJECT_ROOT, rel_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(src, encoding='utf-8')

async def generate_files(files_spec: Dict[str, str]) -> None:
    """Generate only *files_spec* mapping on disk (helper for incremental updates)."""
    for rel_path, src in files_spec.items():
        path = _safe_join(PROJECT_ROOT, rel_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(src, encoding='utf-8')
