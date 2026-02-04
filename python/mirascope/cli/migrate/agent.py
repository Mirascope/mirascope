"""Migration agent that performs v1 to v2 migration."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from mirascope import llm, ops
from mirascope.cli.migrate import ui
from mirascope.cli.migrate.prompts import get_migration_prompt
from mirascope.cli.migrate.tools import MIGRATION_TOOLS, MigrationContext

if TYPE_CHECKING:
    from typing import Any

    from mirascope.llm import ContextStreamResponse, Model


def _get_model_id(requested_model: str) -> str:
    """Get an available model based on API keys present.

    Args:
        requested_model: The model ID requested by the user.

    Returns:
        The model ID to use (may differ if requested provider unavailable).

    Raises:
        SystemExit: If no API key is available.
    """
    provider = requested_model.split("/")[0]

    key_mapping = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
    }

    # Check if requested provider key is available
    if os.getenv(key_mapping.get(provider, "")):
        return requested_model

    # Check for Mirascope API key (works with any provider via router)
    if os.getenv("MIRASCOPE_API_KEY"):
        return requested_model

    # Try other providers
    for prov, key in key_mapping.items():
        if os.getenv(key):
            default_models = {
                "anthropic": "anthropic/claude-sonnet-4-5",
                "openai": "openai/gpt-4o",
                "google": "google/gemini-1.5-pro",
            }
            ui.show_warning(f"No API key for {provider}, using {prov} instead")
            return default_models[prov]

    ui.show_error(
        "No API key found. Set one of: MIRASCOPE_API_KEY, ANTHROPIC_API_KEY, "
        "OPENAI_API_KEY, or GOOGLE_API_KEY"
    )
    raise SystemExit(1)


def _display_tool_call(tool_call: llm.ToolCall, verbose: bool) -> None:
    """Display a tool call to the terminal.

    Args:
        tool_call: The tool call to display.
        verbose: Whether to show verbose output.
    """
    try:
        args = json.loads(tool_call.args)
    except json.JSONDecodeError:
        args = {"raw": tool_call.args}

    ui.show_tool_call(tool_call.name, args, verbose)


@ops.version(name="migration_llm_call")
def _make_migration_call(
    model: Model,
    prompt: str,
    ctx: llm.Context[Any],
    tools: list[Any],
) -> ContextStreamResponse[Any, None]:
    """Version each LLM call for fine-grained evaluation."""
    return model.context_stream(prompt, ctx=ctx, tools=tools)


@ops.version(name="migration_llm_resume")
def _resume_migration_call(
    response: ContextStreamResponse[Any, None],
    ctx: llm.Context[Any],
    tool_outputs: list[Any],
) -> ContextStreamResponse[Any, None]:
    """Version each resumed call."""
    return response.resume(ctx, tool_outputs)


@ops.version(name="migration_agent")
def run_migration_agent(
    path: str,
    model_id: str,
    dry_run: bool,
    auto_approve: bool,
    verbose: bool,
) -> None:
    """Run the migration agent.

    Args:
        path: Path to migrate.
        model_id: Model ID to use (e.g., "anthropic/claude-sonnet-4-5").
        dry_run: Whether to only show what would be done.
        auto_approve: Whether to auto-approve all changes.
        verbose: Whether to show verbose output (thinking, tool calls).
    """
    # Resolve the project root
    project_root = Path(path).resolve()
    if not project_root.exists():
        ui.show_error(f"Path not found: {path}")
        raise SystemExit(1)

    if not project_root.is_dir():
        ui.show_error(f"Path is not a directory: {path}")
        raise SystemExit(1)

    # Validate/resolve model
    actual_model = _get_model_id(model_id)

    # Create migration context
    context = MigrationContext(
        project_root=project_root,
        dry_run=dry_run,
        auto_approve=auto_approve,
        verbose=verbose,
    )

    # Create the LLM context for tools
    ctx = llm.Context(deps=context)

    # Show startup info
    ui.show_progress(f"Starting migration agent with model: {actual_model}")
    ui.show_progress(f"Target path: {project_root}")
    if dry_run:
        ui.show_warning("DRY RUN mode - no files will be modified")
    if auto_approve:
        ui.show_warning("AUTO-APPROVE mode - all changes will be applied automatically")
    ui.console.print()

    # Get the initial prompt
    prompt = get_migration_prompt(
        target_path=str(project_root),
        dry_run=dry_run,
        auto_approve=auto_approve,
    )

    # Create the model and start streaming with context
    model = llm.model(actual_model)
    response = _make_migration_call(model, prompt, ctx, MIGRATION_TOOLS)

    # The agent loop
    while True:
        for stream in response.streams():
            match stream.content_type:
                case "text":
                    for chunk in stream:
                        ui.print_streaming(chunk)
                    ui.console.print()  # Newline after text

                case "thought":
                    if verbose:
                        ui.console.print("\n[dim]<Thinking>[/]")
                        for chunk in stream:
                            ui.show_thinking(chunk)
                        ui.console.print("\n[dim]</Thinking>[/]\n")

                case "tool_call":
                    tool_call = stream.collect()
                    _display_tool_call(tool_call, verbose)

        # Check if we're done
        if not response.tool_calls:
            break

        # Execute tools with context and continue
        tool_outputs = response.execute_tools(ctx)
        response = _resume_migration_call(response, ctx, tool_outputs)

    ui.console.print()
    ui.show_success("Migration agent finished!")
