import json
import tempfile
from pathlib import Path

from mirascope import llm

# For safety, the agent may only operate within this workspace.
WORKSPACE = Path(tempfile.mkdtemp(prefix="agent_"))


def resolve_path(path_str: str) -> Path | None:
    """Resolve a path within the workspace, returning None if it escapes."""
    path = (WORKSPACE / path_str).resolve()
    if WORKSPACE.resolve() not in path.parents and path != WORKSPACE.resolve():
        return None
    return path


@llm.tool
def list_files(directory: str = ".") -> str:
    """List files in a directory."""
    path = resolve_path(directory)
    if path is None:
        return "Error: Path is outside the workspace"
    if not path.exists():
        return f"Directory not found: {directory}"
    files = [f.name + ("/" if f.is_dir() else "") for f in path.iterdir()]
    return "\n".join(files) if files else "(empty directory)"


@llm.tool
def read_file(filepath: str) -> str:
    """Read the contents of a file."""
    path = resolve_path(filepath)
    if path is None:
        return "Error: Path is outside the workspace"
    if not path.exists():
        return f"File not found: {filepath}"
    return path.read_text()


@llm.tool
def write_file(filepath: str, content: str) -> str:
    """Write content to a file."""
    path = resolve_path(filepath)
    if path is None:
        return "Error: Path is outside the workspace"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return f"Wrote {len(content)} bytes to {filepath}"


def display_tool_call(tool_call: llm.ToolCall) -> str:
    args = json.loads(tool_call.args)
    match tool_call.name:
        case "list_files":
            return f"[Tool] List files in '{args.get('directory', '.')}'"
        case "read_file":
            return f"[Tool] Read '{args['filepath']}'"
        case "write_file":
            return f"[Tool] Write '{args['filepath']}'"
        case _:
            return f"[Tool]: {tool_call.name}"


def run_agent(model_id: llm.ModelId, query: str):
    model = llm.model(model_id, thinking={"level": "medium", "include_thoughts": True})
    response = model.stream(query, tools=[list_files, read_file, write_file])

    while True:  # The Agent Loop
        for stream in response.streams():
            match stream.content_type:
                case "text":
                    for chunk in stream:
                        print(chunk, flush=True, end="")
                    print("\n")
                case "thought":
                    print("<Thinking>\n", flush=True)
                    for chunk in stream:
                        print(chunk, flush=True, end="")
                    print("</Thinking>\n", flush=True)
                case "tool_call":
                    tool_call = stream.collect()
                    print(display_tool_call(tool_call) + "\n")

        if not response.tool_calls:
            break  # Agent is finished.

        response = response.resume(response.execute_tools())


run_agent(
    "anthropic/claude-sonnet-4-5",
    "Create a calculator module (calc.py) with add, subtract, multiply, divide "
    "functions, then create a test file (test_calc.py) that tests each function.",
)
print(f"View the agent's work in this directory: {WORKSPACE}\n")
