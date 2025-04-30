import typer
import asyncio
import subprocess
from pathlib import Path

from .services.memory import init_db, register_project, get_project_path, save_spec, log_history
from .services.promptifier import build_spec
from .services.architect import enrich_spec
from .services.updater import get_last_spec, diff_specs
from .services.codegen import generate_project, generate_files

app = typer.Typer()
init_db()

@app.command()
def new(
    name: str = typer.Argument(..., help="Имя проекта (директория)"),
    request: str = typer.Argument(..., help="Начальное NL-описание для генерации кода")
):
    """Создать и зарегистрировать новый проект."""
    project_dir = Path.cwd() / name
    typer.echo(f"📁 Creating project directory: {project_dir}")
    project_dir.mkdir(exist_ok=True)
    pid = register_project(name, str(project_dir))

    async def main():
        typer.echo("🔍 Building spec...")
        spec = await build_spec(request)
        typer.echo("✅ Spec built.")

        typer.echo("📐 Enriching structure...")
        full = await enrich_spec(spec)
        typer.echo("✅ Spec enriched.")

        from .services import codegen
        codegen.PROJECT_ROOT = project_dir
        typer.echo("⚙️ Generating code...")
        await generate_project(full)
        typer.echo(f"✅ Project '{name}' generated in {project_dir}")

        save_spec(pid, full)
        log_history(pid, 'new', {'request': request, 'changed': list(full.get('project_structure', {}).keys())})

    asyncio.run(main())

@app.command()
def go(
    name: str = typer.Argument(..., help="Имя зарегистрированного проекта")
):
    """Показать команду для перехода в каталог проекта."""
    path = get_project_path(name)
    if not path:
        typer.echo(f"❌ No such project: {name}")
        raise typer.Exit(1)
    typer.echo(f"Run: cd {path}")

@app.command()
def do(
    request: str = typer.Argument(..., help="NL-описание для изменения или обновления кода в текущем проекте")
):
    """Выполнить изменения по запросу для текущего проекта и записать историю."""
    project = Path.cwd().name
    path = get_project_path(project)
    if not path:
        typer.echo(f"❌ Unknown project: {project}. Перейдите в каталог проекта или создайте новый через 'vibe new'.")
        raise typer.Exit(1)
    pid = register_project(project, path)

    async def main():
        typer.echo("🔍 Building spec...")
        spec = await build_spec(request)
        typer.echo("✅ Spec built.")

        typer.echo("📐 Enriching structure...")
        full = await enrich_spec(spec)
        typer.echo("✅ Spec enriched.")

        old = get_last_spec(project)
        changed = diff_specs(old, full)
        if not changed:
            typer.echo("❓ Nothing to change.")
            return

        from .services import codegen
        codegen.PROJECT_ROOT = Path(path)
        typer.echo(f"🛠️ Applying changes to {len(changed)} file(s)...")
        await generate_files(full, changed)
        typer.echo("✅ Changes applied.")

        save_spec(pid, full)
        log_history(pid, 'do', {'request': request, 'changed': changed})

        # Запуск тестов только если есть директория tests
        tests_dir = Path(path) / "tests"
        if tests_dir.exists():
            typer.echo("🏃 Running tests...")
            result = subprocess.run(["pytest", "--maxfail=1", "--disable-warnings"], cwd=path)
            if result.returncode == 0:
                typer.echo("✅ All tests passed!")
            else:
                typer.echo("⚠️ Tests failed. Проверьте лог и запустите 'vibe do' заново с более точным запросом.")
        else:
            typer.echo("⚠️ No tests found, skipping test run.")

    asyncio.run(main())

if __name__ == '__main__':
    app()
