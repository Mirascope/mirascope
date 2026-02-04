"""Migrate CLI - Migrate Mirascope v1 code to v2."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from mirascope import ops

app = typer.Typer(
    name="migrate",
    help="Migrate Mirascope v1 code to v2",
    invoke_without_command=True,
)

DEFAULT_MODEL = "anthropic/claude-sonnet-4-5"


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    path: Annotated[
        str | None,
        typer.Option("--path", "-p", help="Path to migrate (file or directory)"),
    ] = None,
    model: Annotated[
        str,
        typer.Option("--model", "-m", help="Model to use for migration"),
    ] = DEFAULT_MODEL,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", help="Show what would be done without making changes"
        ),
    ] = False,
    auto_approve: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Auto-approve all changes (no prompts)"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v", help="Show detailed progress (thinking, tool calls)"
        ),
    ] = False,
) -> None:
    """Migrate Mirascope v1 code to v2.

    The agent will scan for v1 patterns and interactively migrate your code
    with approval prompts. Git operations (branching, committing) should be
    done by you before/after running the migration.

    Examples:

        # Migrate current directory
        mirascope migrate

        # Migrate a specific project
        mirascope migrate --path ./my-project

        # Dry run to see what would change
        mirascope migrate --dry-run

        # Auto-approve all changes
        mirascope migrate --yes

        # Use a different model
        mirascope migrate --model openai/gpt-4o

        # Scan only (no changes)
        mirascope migrate scan ./my-project
    """
    # Only run if no subcommand was invoked
    if ctx.invoked_subcommand is None:
        # Configure ops for tracing to Mirascope Cloud if API key is available
        if os.getenv("MIRASCOPE_API_KEY"):
            ops.configure()

        from mirascope.cli.migrate.agent import run_migration_agent

        run_migration_agent(
            path=path or ".",
            model_id=model,
            dry_run=dry_run,
            auto_approve=auto_approve,
            verbose=verbose,
        )


@app.command("scan")
def scan(
    path: Annotated[
        str,
        typer.Argument(help="Path to scan for v1 patterns"),
    ] = ".",
) -> None:
    """Scan for v1 patterns without making changes.

    Reports files that need migration and the patterns found.
    This is useful for understanding the scope of migration before running it.

    Examples:

        # Scan current directory
        mirascope migrate scan

        # Scan a specific project
        mirascope migrate scan ./my-project
    """
    from mirascope.cli.migrate import ui
    from mirascope.cli.migrate.patterns import (
        scan_directory_for_patterns,
        summarize_patterns,
    )

    target = Path(path).resolve()

    if not target.exists():
        ui.show_error(f"Path not found: {path}")
        raise typer.Exit(1)

    if not target.is_dir():
        ui.show_error(f"Path is not a directory: {path}")
        raise typer.Exit(1)

    ui.show_progress(f"Scanning {target} for v1 patterns...")

    # Count total Python files
    total_files = len(list(target.glob("**/*.py")))

    # Scan for patterns
    results = scan_directory_for_patterns(target)
    summary = summarize_patterns(results)

    # Display results
    ui.show_scan_results(results, summary, total_files)

    if results:
        ui.console.print()
        ui.console.print(
            "[bold]Run [cyan]mirascope migrate[/cyan] to start the migration.[/]"
        )
