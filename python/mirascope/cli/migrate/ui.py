"""Terminal UI helpers for the migration CLI."""

from __future__ import annotations

import difflib
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

if TYPE_CHECKING:
    from mirascope.cli.migrate.patterns import LegacyPattern

console = Console()


def show_progress(message: str, style: str = "bold blue") -> None:
    """Show a progress message.

    Args:
        message: The message to display.
        style: Rich style for the prefix.
    """
    console.print(f"[{style}]>>>[/] {message}")


def show_error(message: str) -> None:
    """Show an error message.

    Args:
        message: The error message.
    """
    console.print(f"[bold red]Error:[/] {message}")


def show_success(message: str) -> None:
    """Show a success message.

    Args:
        message: The success message.
    """
    console.print(f"[bold green]Success:[/] {message}")


def show_warning(message: str) -> None:
    """Show a warning message.

    Args:
        message: The warning message.
    """
    console.print(f"[bold yellow]Warning:[/] {message}")


def print_streaming(text: str, end: str = "", flush: bool = True) -> None:
    """Print streaming text without newline by default.

    Args:
        text: Text to print.
        end: String to append (default empty).
        flush: Whether to flush output.
    """
    console.print(text, end=end)


def show_diff(filepath: str, old_content: str, new_content: str) -> str:
    """Show a unified diff between old and new content.

    Args:
        filepath: The file being modified.
        old_content: The original content.
        new_content: The proposed new content.

    Returns:
        The diff as a string.
    """
    diff_lines = list(
        difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{filepath}",
            tofile=f"b/{filepath}",
        )
    )

    diff_text = "".join(diff_lines)

    if diff_text:
        syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=False)
        console.print(
            Panel(syntax, title=f"[bold]Changes to {filepath}[/]", border_style="blue")
        )
    else:
        console.print(f"[dim]No changes to {filepath}[/]")

    return diff_text


def ask_approval(filepath: str, old_content: str, new_content: str) -> str:
    """Show diff and ask for user approval.

    Args:
        filepath: The file being modified.
        old_content: The original content.
        new_content: The proposed new content.

    Returns:
        'approve', 'reject', or user's feedback text.
    """
    show_diff(filepath, old_content, new_content)

    response = Prompt.ask(
        "\n[bold]Apply these changes?[/]",
        choices=["y", "n", "feedback"],
        default="y",
    )

    if response == "y":
        return "approve"
    elif response == "n":
        return "reject"
    else:
        feedback = Prompt.ask("[bold]Enter your feedback[/]")
        return f"feedback: {feedback}"


def ask_question(question: str, choices: list[str] | None = None) -> str:
    """Ask the user a question.

    Args:
        question: The question to ask.
        choices: Optional list of choices.

    Returns:
        The user's response.
    """
    if choices:
        return Prompt.ask(f"[bold]{question}[/]", choices=choices)
    return Prompt.ask(f"[bold]{question}[/]")


def ask_yes_no(question: str, default: bool = True) -> bool:
    """Ask a yes/no question.

    Args:
        question: The question to ask.
        default: Default answer.

    Returns:
        True for yes, False for no.
    """
    return Confirm.ask(f"[bold]{question}[/]", default=default)


def show_scan_results(
    results: dict[str, list[LegacyPattern]], summary: dict[str, int], total_files: int
) -> None:
    """Display scan results in a formatted table.

    Args:
        results: Dictionary of file paths to pattern lists.
        summary: Summary of pattern counts by type.
        total_files: Total number of files scanned.
    """
    console.print()
    console.print(
        f"[bold]Scanned {total_files} files, found {len(results)} with legacy patterns[/]"
    )
    console.print()

    if not results:
        console.print(
            "[green]No legacy patterns found - your code may already be v2![/]"
        )
        return

    # Summary table
    summary_table = Table(title="Pattern Summary", show_header=True)
    summary_table.add_column("Pattern Type", style="cyan")
    summary_table.add_column("Count", justify="right", style="magenta")

    for pattern_type, count in sorted(summary.items(), key=lambda x: -x[1]):
        summary_table.add_row(pattern_type.replace("_", " ").title(), str(count))

    console.print(summary_table)
    console.print()

    # Detailed results
    details_table = Table(title="Files Requiring Migration", show_header=True)
    details_table.add_column("File", style="cyan", no_wrap=True)
    details_table.add_column("Line", justify="right", style="yellow")
    details_table.add_column("Pattern", style="magenta")
    details_table.add_column("Match", style="dim")

    for filepath, patterns in sorted(results.items()):
        for i, pattern in enumerate(patterns[:5]):  # Limit to 5 per file
            file_display = filepath if i == 0 else ""
            details_table.add_row(
                file_display,
                str(pattern.line),
                pattern.pattern_type.replace("_", " ").title(),
                pattern.match[:50] + "..."
                if len(pattern.match) > 50
                else pattern.match,
            )
        if len(patterns) > 5:
            details_table.add_row("", "", f"... and {len(patterns) - 5} more", "")

    console.print(details_table)


def show_tool_call(tool_name: str, args: dict[str, Any], verbose: bool = False) -> None:
    """Display a tool call.

    Args:
        tool_name: Name of the tool being called.
        args: Arguments to the tool.
        verbose: Whether to show full details.
    """
    if verbose:
        console.print(f"\n[dim][Tool: {tool_name}][/]")
        for key, value in args.items():
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."
            console.print(f"[dim]  {key}: {value_str}[/]")
    else:
        # Compact display
        match tool_name:
            case "list_files":
                console.print(
                    f"[dim]>>> Listing files in {args.get('directory', '.')}[/]"
                )
            case "read_file":
                console.print(f"[dim]>>> Reading {args.get('filepath')}[/]")
            case "write_file":
                console.print(f"[dim]>>> Writing {args.get('filepath')}[/]")
            case "run_command":
                cmd = args.get("command", "")
                console.print(
                    f"[dim]>>> Running: {cmd[:60]}{'...' if len(cmd) > 60 else ''}[/]"
                )
            case "search_codebase":
                console.print(f"[dim]>>> Searching for: {args.get('pattern')}[/]")
            case _:
                console.print(f"[dim]>>> {tool_name}[/]")


def show_thinking(content: str) -> None:
    """Display agent thinking in a muted style.

    Args:
        content: The thinking content.
    """
    console.print(f"[dim italic]{content}[/]", end="")
