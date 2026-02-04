"""Agent tools for the migration CLI."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from mirascope import llm
from mirascope.cli.migrate import ui


@dataclass
class MigrationContext:
    """Context for the migration agent."""

    project_root: Path
    dry_run: bool = False
    auto_approve: bool = False
    verbose: bool = False


def _resolve_path(ctx: MigrationContext, path_str: str) -> Path | None:
    """Resolve a path within the project root, returning None if it escapes.

    Args:
        ctx: Migration context with project root.
        path_str: Path string to resolve.

    Returns:
        Resolved path or None if outside project root.
    """
    path = (ctx.project_root / path_str).resolve()
    root = ctx.project_root.resolve()

    if root not in path.parents and path != root:
        return None
    return path


# Allowlisted commands for security
ALLOWED_COMMANDS = frozenset(
    {
        "pyright",
        "ruff",
        "python",
    }
)

# Git commands that are safe (read-only / inspection only)
ALLOWED_GIT_SUBCOMMANDS = frozenset(
    {
        "status",
        "diff",
        "log",
        "show",
        "branch",
        "rev-parse",
        "ls-files",
        "ls-tree",
    }
)


def _is_command_allowed(command: str) -> bool:
    """Check if a command is in the allowlist.

    Args:
        command: The command to check.

    Returns:
        True if allowed, False otherwise.
    """
    parts = command.strip().split()
    if not parts:
        return False

    cmd = parts[0]

    # Handle git commands specially - only allow read-only subcommands
    if cmd == "git":
        if len(parts) < 2:
            return False
        subcommand = parts[1]
        return subcommand in ALLOWED_GIT_SUBCOMMANDS

    return cmd in ALLOWED_COMMANDS


@llm.tool
def list_files(
    ctx: llm.Context[MigrationContext],
    directory: str = ".",
    pattern: str = "**/*.py",
) -> str:
    """List files in a directory matching a glob pattern.

    Args:
        ctx: Migration context.
        directory: The directory to search (relative to project root).
        pattern: Glob pattern to match files. Default is all Python files.

    Returns:
        Newline-separated list of file paths relative to project root, or error.
    """
    path = _resolve_path(ctx.deps, directory)
    if path is None:
        return f"Error: Path '{directory}' is outside the project root"

    if not path.exists():
        return f"Error: Directory not found: {directory}"

    if not path.is_dir():
        return f"Error: Not a directory: {directory}"

    try:
        files = sorted(path.glob(pattern))
        # Return paths relative to project root
        relative_paths: list[str] = []
        for f in files:
            if f.is_file():
                try:
                    rel_path = f.relative_to(ctx.deps.project_root)
                    relative_paths.append(str(rel_path))
                except ValueError:
                    continue

        if not relative_paths:
            return f"No files matching '{pattern}' found in {directory}"

        return "\n".join(relative_paths)
    except Exception as e:
        return f"Error listing files: {e}"


@llm.tool
def read_file(ctx: llm.Context[MigrationContext], filepath: str) -> str:
    """Read the contents of a file.

    Args:
        ctx: Migration context.
        filepath: Path to the file relative to project root.

    Returns:
        The file contents, or an error message if not found.
    """
    path = _resolve_path(ctx.deps, filepath)
    if path is None:
        return f"Error: Path '{filepath}' is outside the project root"

    if not path.exists():
        return f"Error: File not found: {filepath}"

    if not path.is_file():
        return f"Error: Not a file: {filepath}"

    try:
        content = path.read_text()
        return content
    except UnicodeDecodeError:
        return f"Error: Cannot read binary file: {filepath}"
    except Exception as e:
        return f"Error reading file: {e}"


@llm.tool
def write_file(ctx: llm.Context[MigrationContext], filepath: str, content: str) -> str:
    """Write content to a file, creating directories if needed.

    In dry-run mode, this will only show what would be written.

    Args:
        ctx: Migration context.
        filepath: Path to write to (relative to project root).
        content: The new file content.

    Returns:
        Success message with bytes written, or error message.
    """
    path = _resolve_path(ctx.deps, filepath)
    if path is None:
        return f"Error: Path '{filepath}' is outside the project root"

    if ctx.deps.dry_run:
        return f"[DRY RUN] Would write {len(content)} bytes to {filepath}"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return f"Successfully wrote {len(content)} bytes to {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"


@llm.tool
def run_command(ctx: llm.Context[MigrationContext], command: str) -> str:
    """Run a shell command and return the output.

    Only certain commands are allowed: git, pyright, ruff, python

    Args:
        ctx: Migration context.
        command: The shell command to run.

    Returns:
        Command output (stdout + stderr), or error message.
    """
    if not _is_command_allowed(command):
        return (
            f"Error: Command not allowed. Only these commands are permitted: "
            f"{', '.join(sorted(ALLOWED_COMMANDS))} and git (read-only operations)"
        )

    if ctx.deps.dry_run and not command.startswith(
        ("git status", "git diff", "git log", "pyright")
    ):
        return f"[DRY RUN] Would run: {command}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=ctx.deps.project_root,
            capture_output=True,
            text=True,
            timeout=120,
        )

        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr if output else result.stderr

        if result.returncode != 0:
            output += f"\n[Exit code: {result.returncode}]"

        return output.strip() if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 120 seconds"
    except Exception as e:
        return f"Error running command: {e}"


@llm.tool
def search_codebase(
    ctx: llm.Context[MigrationContext],
    pattern: str,
    file_pattern: str = "*.py",
    max_results: int = 50,
) -> str:
    """Search the codebase for a regex pattern.

    Args:
        ctx: Migration context.
        pattern: Regex pattern to search for.
        file_pattern: Glob pattern to filter files.
        max_results: Maximum number of results to return.

    Returns:
        Matches with file:line:content format, limited to max_results.
    """
    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"Error: Invalid regex pattern: {e}"

    results: list[str] = []
    root = ctx.deps.project_root

    for filepath in root.glob(f"**/{file_pattern}"):
        if not filepath.is_file():
            continue

        # Skip common non-source directories
        parts = filepath.parts
        if any(
            p in {".git", ".venv", "venv", "__pycache__", "node_modules", ".tox"}
            for p in parts
        ):
            continue

        try:
            content = filepath.read_text()
        except (UnicodeDecodeError, OSError):
            continue

        for line_num, line in enumerate(content.splitlines(), start=1):
            if regex.search(line):
                rel_path = filepath.relative_to(root)
                results.append(f"{rel_path}:{line_num}:{line.strip()}")

                if len(results) >= max_results:
                    results.append(f"... (truncated at {max_results} results)")
                    return "\n".join(results)

    if not results:
        return f"No matches found for pattern: {pattern}"

    return "\n".join(results)


@llm.tool
def ask_user(
    ctx: llm.Context[MigrationContext],
    question: str,
    choices: list[str] | None = None,
) -> str:
    """Ask the user a question and wait for their response.

    Use this when you need clarification or approval for something.

    Args:
        ctx: Migration context.
        question: The question to ask.
        choices: Optional list of choices (user can also type freely).

    Returns:
        The user's response.
    """
    if ctx.deps.auto_approve:
        default = choices[0] if choices else "yes"
        return f"[AUTO-APPROVED] {default}"

    return ui.ask_question(question, choices)


@llm.tool
def show_diff_and_approve(
    ctx: llm.Context[MigrationContext],
    filepath: str,
    old_content: str,
    new_content: str,
) -> str:
    """Show a diff between old and new content and ask for user approval.

    Args:
        ctx: Migration context.
        filepath: The file being modified.
        old_content: The original content.
        new_content: The proposed new content.

    Returns:
        'approve', 'reject', or feedback from the user.
    """
    if ctx.deps.auto_approve:
        ui.show_diff(filepath, old_content, new_content)
        return "approve"

    return ui.ask_approval(filepath, old_content, new_content)


# Export all tools for the agent
MIGRATION_TOOLS = [
    list_files,
    read_file,
    write_file,
    run_command,
    search_codebase,
    ask_user,
    show_diff_and_approve,
]
