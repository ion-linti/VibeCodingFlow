import json
from pathlib import Path
from .openai_client import chat
from ..prompts import PROMPT_CODEGEN_PROJECT_SYSTEM, PROMPT_CODEGEN_PROJECT_USER

# Корневая папка для генерации кода; переназначается в CLI
PROJECT_ROOT = Path('.')

async def generate_project(spec_full: dict) -> None:
    """
    Генерирует все файлы по полной спецификации:
    - Запрашивает у LLM JSON mapping пути → содержимое файлов
    - Пишет каждый файл под PROJECT_ROOT
    """
    # Формируем запрос
    raw = await chat(
        PROMPT_CODEGEN_PROJECT_USER.format(
            project_spec=json.dumps(
                spec_full.get('project_structure', {}),
                ensure_ascii=False
            )
        ),
        system=PROMPT_CODEGEN_PROJECT_SYSTEM,
        model='gpt-4o',
        temperature=0.4
    )

    # Извлекаем JSON-объект из ответа
    start = raw.find('{')
    if start == -1:
        raise ValueError(f'No JSON found in CodeGen response: {raw!r}')

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
        raise ValueError(f'Unmatched braces in CodeGen response: {raw!r}')

    files = json.loads(raw[start:end])

    # Пишем файлы на диск, пропуская указания каталогов
    for rel_path, src in files.items():
        # Пропускаем корень и записи-папки
        if rel_path in ('/', '.', '') or rel_path.endswith('/'):
            continue
        # Нормализуем путь: убираем ведущие / и \
        rel = rel_path.lstrip('/\\')
        path = PROJECT_ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(src, encoding='utf-8')

async def generate_files(spec_full: dict, changed: list[str]) -> None:
    """
    Инкрементально обновляет только изменённые файлы.
    Формируем поднабор спецификации и вызываем generate_project.
    """
    subset = {k: spec_full['project_structure'][k] for k in changed}
    await generate_project({'project_structure': subset})
