import typer
import asyncio
import subprocess
from pathlib import Path

from .services.memory import (
    init_db,
    register_project,
    get_project_path,
    save_spec,
    log_history,
)
from .services.promptifier import build_spec
from .services.architect import enrich_spec
from .services.updater import get_last_spec, diff_specs
from .services.codegen import generate_project, generate_files

app = typer.Typer()
init_db()


@app.command()
def new(
    name: str = typer.Argument(..., help="Project name (directory)"),
    request: str = typer.Argument(..., help="Initial NL description for generating code"),
):
    """Create and register a new project."""
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
        log_history(pid, "new", {"request": request, "changed": list(full.get("project_structure", {}).keys())})

    asyncio.run(main())


@app.command()
def go(
    name: str = typer.Argument(..., help="Name of the registered project"),
):
    """Show the command to navigate to the project directory."""
    path = get_project_path(name)
    if not path:
        typer.echo(f"❌ No such project: {name}")
        raise typer.Exit(1)
    typer.echo(f"Run: cd {path}")


@app.command()
def do(
    request: str = typer.Argument(
        ..., help="NL description for modifying or updating the code in the current project"
    )
):
    """Apply changes based on the request for the current project and log the history."""
    project = Path.cwd().name
    path = get_project_path(project)
    if not path:
        typer.echo(
            f"❌ Unknown project: {project}. Navigate to the project directory or create a new one using 'vibe new'."
        )
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
        # FIX: generate_files теперь вызываем только с одним аргументом
        await generate_files(full)
        typer.echo("✅ Changes applied.")

        save_spec(pid, full)
        log_history(pid, "do", {"request": request, "changed": changed})

        tests_dir = Path(path) / "tests"
        if tests_dir.exists():
            typer.echo("🏃 Running tests...")
            result = subprocess.run(["pytest", "--maxfail=1", "--disable-warnings"], cwd=path)
            if result.returncode == 0:
                typer.echo("✅ All tests passed!")
            else:
                typer.echo("⚠️ Tests failed. Check the log and run 'vibe do' again with a more specific request.")
        else:
            typer.echo("⚠️ No tests found, skipping test run.")

    asyncio.run(main())


if __name__ == "__main__":
    app()
