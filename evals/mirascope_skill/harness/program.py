"""Run, validate, and query generated Mirascope programs via subprocess."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def _run_uv(program_path: str | Path, *args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    # Pass through API keys to subprocesses
    env = os.environ.copy()
    return subprocess.run(
        ["uv", "run", str(program_path), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def validate_program(program_path: str | Path) -> tuple[bool, str]:
    """Run --help and --schema to verify the program is well-formed.

    Returns (success, error_message).
    """
    path = Path(program_path)
    if not path.exists():
        return False, f"Program file not found: {path}"

    # Check --help
    try:
        result = _run_uv(path, "--help")
        if result.returncode != 0:
            return False, f"--help failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "--help timed out"

    # Check --schema
    try:
        result = _run_uv(path, "--schema")
        if result.returncode != 0:
            return False, f"--schema failed: {result.stderr}"
        schema = json.loads(result.stdout)
        if "input" not in schema or "output" not in schema:
            return False, f"--schema missing 'input' or 'output' keys: {list(schema.keys())}"
    except subprocess.TimeoutExpired:
        return False, "--schema timed out"
    except json.JSONDecodeError as e:
        return False, f"--schema returned invalid JSON: {e}"

    return True, ""


def get_schema(program_path: str | Path) -> dict:
    """Run --schema and return the parsed JSON."""
    result = _run_uv(program_path, "--schema")
    if result.returncode != 0:
        raise RuntimeError(f"--schema failed: {result.stderr}")
    return json.loads(result.stdout)


def run_program(program_path: str | Path, input_json: str, timeout: int = 120) -> tuple[str, str]:
    """Run --input and return (stdout, stderr)."""
    result = _run_uv(program_path, "--input", input_json, timeout=timeout)
    return result.stdout, result.stderr
