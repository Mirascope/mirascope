"""Stubs command for generating type stubs for functions decorated with lilypad.generation."""

import ast
import importlib
import inspect
import json
import os
import sys
from pathlib import Path
from textwrap import dedent
from typing import Any, TypeAlias

import typer
from lilypad_sdk import LilypadSDK
from lilypad_sdk.types.ee.projects import GenerationPublic
from rich import print
from rich.console import Console
from rich.table import Table

from ... import _utils
from ...generations import (
    clear_registry,
    disable_recording,
    enable_recording,
    get_decorated_functions,
)

app = typer.Typer()
console = Console()
DEBUG: bool = False

FilePath: TypeAlias = str
ModulePath: TypeAlias = str
FunctionInfo: TypeAlias = tuple[str, str, int, str]

DEFAULT_DIRECTORY: Path = typer.Argument(
    Path("."),
    help="Directory to scan forfrom lilypad_sdk.types.projects.generations import SpanPublic decorated functions.",
)
DEFAULT_EXCLUDE: list[str] | None = typer.Option(
    None, "--exclude", "-e", help="Comma-separated list of directories to exclude."
)
DEFAULT_VERBOSE: bool = typer.Option(
    False, "--verbose", "-v", help="Show verbose output."
)


def _find_python_files(
    directory: str, exclude_dirs: set[str] | None = None
) -> list[FilePath]:
    if exclude_dirs is None:
        exclude_dirs = {
            "venv",
            ".venv",
            "env",
            ".git",
            ".github",
            "__pycache__",
            "build",
            "dist",
        }
    python_files: list[FilePath] = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def _module_path_from_file(
    file_path: FilePath, base_dir: str | None = None
) -> ModulePath:
    rel_path = os.path.relpath(file_path, base_dir) if base_dir else file_path
    if rel_path.endswith(".py"):
        rel_path = rel_path[:-3]
    return rel_path.replace(os.sep, ".")


def _import_module_safely(module_path: ModulePath) -> bool:
    try:
        importlib.import_module(module_path)
        return True
    except (ImportError, SyntaxError) as e:
        print(f"Warning: Failed to import {module_path}: {e}", file=sys.stderr)
        return False


def _normalize_signature(signature_text: str) -> str:
    # Return only the function definition line (ignoring import lines and decorators)
    lines = signature_text.splitlines()
    func_lines = [
        line.strip()
        for line in lines
        if line.strip().startswith("def ") or line.strip().startswith("async def ")
    ]
    if not func_lines:
        func_lines = [
            line.strip() for line in lines if not line.strip().startswith("@")
        ]
    normalized = " ".join(func_lines).strip()
    if normalized.endswith("..."):
        normalized = normalized[:-3] + " pass"
    if normalized.endswith(":"):
        normalized += " pass"
    if DEBUG:
        print(f"[DEBUG] Normalized signature: {normalized}")
    return normalized


def _parse_parameters_from_signature(signature_text: str) -> list[str]:
    try:
        normalized = _normalize_signature(signature_text)
        module = ast.parse(normalized)
        func_def = module.body[0]
        params: list[str] = []
        total_args = func_def.args.args  # pyright: ignore [reportAttributeAccessIssue]
        defaults = func_def.args.defaults  # pyright: ignore [reportAttributeAccessIssue]
        num_defaults = len(defaults)
        start_default = len(total_args) - num_defaults
        for i, arg in enumerate(total_args):
            param_str = arg.arg
            if arg.annotation is not None:
                try:
                    annotation = ast.unparse(arg.annotation)
                except Exception:
                    annotation = "Any"
                param_str += f": {annotation}"
            if i >= start_default:
                default_node = defaults[i - start_default]
                try:
                    default_val = ast.unparse(default_node)
                except Exception:
                    default_val = "..."
                param_str += f" = {default_val}"
            params.append(param_str)
        if func_def.args.vararg:  # pyright: ignore [reportAttributeAccessIssue]
            vararg = func_def.args.vararg  # pyright: ignore [reportAttributeAccessIssue]
            vararg_str = f"*{vararg.arg}"
            if vararg.annotation:
                try:
                    annotation = ast.unparse(vararg.annotation)
                except Exception:
                    annotation = "Any"
                vararg_str += f": {annotation}"
            params.append(vararg_str)
        if func_def.args.kwarg:  # pyright: ignore [reportAttributeAccessIssue]
            kwarg = func_def.args.kwarg  # pyright: ignore [reportAttributeAccessIssue]
            kwarg_str = f"**{kwarg.arg}"
            if kwarg.annotation:
                try:
                    annotation = ast.unparse(kwarg.annotation)
                except Exception:
                    annotation = "Any"
                kwarg_str += f": {annotation}"
            params.append(kwarg_str)
        if DEBUG:
            print(
                f"[DEBUG] Parsed parameters from normalized signature:\n{normalized}\n=> {params}"
            )
        return params
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Error parsing parameters: {e}")
        return []


def _extract_type_from_param(param: str) -> str:
    parts = param.split(":", 1)
    if len(parts) < 2:
        return "Any"
    rest = parts[1].strip()
    type_part = rest.split("=")[0].strip() if "=" in rest else rest
    return type_part


def _merge_parameters(signature_text: str, arg_types_val: Any) -> list[str]:  # noqa: ANN401
    params_list = _parse_parameters_from_signature(signature_text)
    if isinstance(arg_types_val, dict):
        arg_types_dict = arg_types_val
    else:
        try:
            arg_types_dict = json.loads(arg_types_val)
        except Exception as e:
            if DEBUG:
                print(f"[DEBUG] Error loading arg_types: {e}")
            arg_types_dict = {}
    merged: list[str] = []
    for param in params_list:
        parts = param.split(":", 1)
        name = parts[0].strip()
        default_part = None
        if len(parts) > 1:
            type_and_default = parts[1].strip()
            if "=" in type_and_default:
                type_part, default_part = type_and_default.split("=", 1)
                type_part = type_part.strip()
                default_part = default_part.strip()
            else:
                type_part = type_and_default
        else:
            type_part = "Any"
        new_type = arg_types_dict.get(name, type_part)
        if default_part:
            merged.append(f"{name}: {new_type} = {default_part}")
        else:
            merged.append(f"{name}: {new_type}")
    if DEBUG:
        print(
            f"[DEBUG] Merged parameters for signature:\n{signature_text}\narg_types: {arg_types_val}\n=> {merged}"
        )
    return merged


def _parse_return_type(signature_text: str) -> str:
    try:
        normalized = _normalize_signature(signature_text)
        module = ast.parse(normalized)
        func_def = module.body[0]
        if func_def.returns is not None:  # pyright: ignore [reportAttributeAccessIssue]
            ret = ast.unparse(func_def.returns).strip()  # pyright: ignore [reportAttributeAccessIssue]
        else:
            ret = "Any"
        if DEBUG:
            print(
                f"[DEBUG] Parsed return type from normalized signature: {normalized} => {ret}"
            )
        return ret
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Error parsing return type: {e}")
        return "Any"


def _format_return_type(ret_type: str, is_async: bool) -> str:
    return f"Coroutine[Any, Any, {ret_type}]" if is_async else ret_type


def _extract_parameter_types(merged_params: list[str]) -> list[str]:
    types = [_extract_type_from_param(param) for param in merged_params]
    if DEBUG:
        print(
            f"[DEBUG] Extracted parameter types from merged params: {merged_params} => {types}"
        )
    return types


def _generate_protocol_stub_content(
    func_name: str, versions: list[GenerationPublic], is_async: bool
) -> str:
    if not versions:
        return ""
    sorted_versions = sorted(versions, key=lambda v: v.version_num or 0)
    latest_version = sorted_versions[-1]
    ret_type_latest = _parse_return_type(latest_version.signature)
    class_name = "".join(word.title() for word in func_name.split("_"))
    version_protocols = []
    version_overloads = []
    for version in sorted_versions:
        if version.version_num is None:
            continue
        merged_params = (
            _merge_parameters(version.signature, version.arg_types)
            if version.arg_types
            else _parse_parameters_from_signature(version.signature)
        )
        params_str = ", ".join(merged_params)
        ret_type = _parse_return_type(version.signature)
        ret_type_formatted = (
            f"Coroutine[Any, Any, {ret_type}]" if is_async else ret_type
        )
        version_class_name = f"{class_name}Version{version.version_num}"
        ver_proto = (
            f"class {version_class_name}(Protocol):\n"
            f"    def __call__(self, {params_str}) -> {ret_type_formatted}: ..."
        )
        version_protocols.append(ver_proto)
        _extract_parameter_types(merged_params)
        overload = (
            f"    @classmethod\n"
            f"    @overload\n"
            f"    def version(cls, forced_version: Literal[{version.version_num}], sandbox_runner: SandboxRunner | None = None) -> {version_class_name}: ..."
        )
        version_overloads.append(overload)
    main_ret_type = (
        f"Coroutine[Any, Any, {ret_type_latest}]" if is_async else ret_type_latest
    )
    main_call = f"    def __call__(self) -> {main_ret_type}: ..."
    base_version = (
        f"    @classmethod  # type: ignore[misc]\n"
        f"    def version(cls, forced_version: int, sandbox_runner: SandboxRunner | None = None) -> Callable[..., "
        f"{'Coroutine[Any, Any, Any]' if is_async else 'Any'}]: ..."
    )
    header_types = (
        "overload, Literal, Callable, Any, Protocol, Coroutine"
        if is_async
        else "overload, Literal, Callable, Any, Protocol"
    )
    joined_protocols = "\n\n".join(version_protocols)
    joined_overloads = "\n\n".join(version_overloads)
    content = f"""# This file was auto-generated by lilypad stubs command
from typing import {header_types}
from lilypad.sandbox import SandboxRunner


{joined_protocols}

class {class_name}(Protocol):

{main_call}

{joined_overloads}

{base_version}

{func_name} = {class_name}
"""
    if DEBUG:
        print(f"[DEBUG] Generated stub content for function '{func_name}':\n{content}")
    return dedent(content)


def stubs_command(
    directory: Path = DEFAULT_DIRECTORY,
    exclude: list[str] | None = DEFAULT_EXCLUDE,
    verbose: bool = DEFAULT_VERBOSE,
    debug: bool = False,
) -> None:
    """Generate type stubs for functions decorated with lilypad.generation."""
    global DEBUG
    DEBUG = debug
    if not isinstance(exclude, list):
        exclude = []
    exclude_dirs: set[str] = {
        "venv",
        ".venv",
        "env",
        ".git",
        ".github",
        "__pycache__",
        "build",
        "dist",
    }
    for item in exclude:
        for dir_name in item.split(","):
            exclude_dirs.add(dir_name.strip())
    dir_str: str = str(directory.absolute())
    with console.status(
        "Scanning for functions decorated with [bold]lilypad.generation[/bold]..."
    ):
        python_files: list[FilePath] = _find_python_files(dir_str, exclude_dirs)
        if not python_files:
            print(f"No Python files found in {dir_str}")
            return
        directory_abs: str = os.path.abspath(dir_str)
        parent_dir: str = os.path.dirname(directory_abs)
        sys.path.insert(0, parent_dir)
        enable_recording()
        try:
            for file_path in python_files:
                module_path: ModulePath = _module_path_from_file(file_path, parent_dir)
                _import_module_safely(module_path)
            results = get_decorated_functions("lilypad.generation")
        finally:
            disable_recording()
            clear_registry()
            sys.path.pop(0)
    settings = _utils.load_settings()
    if not settings.api_key or not settings.project_id:
        print(
            "Please set LILYPAD_API_KEY and LILYPAD_PROJECT_ID environment variables."
        )
        return
    client = LilypadSDK(api_key=settings.api_key, base_url=settings.api_base_url)
    decorator_name = "lilypad.generation"
    functions = results.get(decorator_name, [])
    if not functions:
        print(f"No functions found with decorator [bold]{decorator_name}[/bold]")
        return
    print(
        f"\nFound [bold green]{len(functions)}[/bold green] function(s) with decorator [bold]{decorator_name}[/bold]"
    )
    table = Table(show_header=True)
    table.add_column("Source File", style="cyan")
    table.add_column("Functions", style="green")
    table.add_column("Versions", style="yellow")
    file_stub_map: dict[str, list[str]] = {}
    file_func_map: dict[str, list[str]] = {}
    for file_path, function_name, _lineno, module_name in sorted(
        functions, key=lambda x: x[0]
    ):
        try:
            mod = importlib.import_module(module_name)
            fn = getattr(mod, function_name)
            is_async = inspect.iscoroutinefunction(fn)
        except Exception as e:
            print(
                f"[red]Error retrieving function {function_name} from {module_name}: {e}[/red]"
            )
            continue
        try:
            with console.status(
                f"Fetching versions for [bold]{function_name}[/bold]..."
            ):
                versions = client.ee.projects.generations.name.get_by_name(
                    fn.__name__, project_uuid=settings.project_id
                )
            if not versions:
                print(f"[yellow]No versions found for {function_name}[/yellow]")
                continue
            stub_content = _utils.run_ruff(
                dedent(
                    _generate_protocol_stub_content(function_name, versions, is_async)
                )
            ).strip()
            file_stub_map.setdefault(file_path, []).append(stub_content)
            file_func_map.setdefault(file_path, []).append(function_name)
            table.add_row(file_path, function_name, str(len(versions)))
            if verbose:
                print(f"\n[blue]Stub content for {function_name}:[/blue]")
                print(f"[dim]{stub_content}[/dim]")
        except Exception as e:
            print(f"[red]Error processing {function_name}: {e}[/red]")
    for src_file, stubs in file_stub_map.items():
        merged_imports: set[str] = set()
        for stub in stubs:
            lines = stub.splitlines()
            for line in lines:
                if line.startswith("from typing import"):
                    imported = line.split("import", 1)[1].strip()
                    for token in imported.split(","):
                        merged_imports.add(token.strip())
                    break
        base_symbols = {"overload", "Literal", "Callable", "Any", "Protocol"}
        merged_imports |= base_symbols
        for stub in stubs:
            if "Coroutine" in stub:
                merged_imports.add("Coroutine")
                break
        merged_imports_str = ", ".join(sorted(merged_imports))

        new_header = [
            "# This file was auto-generated by lilypad stubs command",
            f"from typing import {merged_imports_str}",
            "from lilypad.sandbox import SandboxRunner",
            "",
        ]
        content_parts = []
        for stub in stubs:
            lines = stub.splitlines()
            idx = 0
            for i, line in enumerate(lines):
                if line.startswith("class "):
                    idx = i
                    break
            content_parts.append("\n".join(lines[idx:]))
        final_content = "\n".join(new_header) + "\n\n" + "\n\n".join(content_parts)
        stub_file = Path(src_file).with_suffix(".pyi")
        stub_file.parent.mkdir(parents=True, exist_ok=True)
        stub_file.write_text(final_content, encoding="utf-8")
    print(f"\nGenerated stub files for {len(file_stub_map)} source file(s).")
    console.print(table)


if __name__ == "__main__":
    app.command()(stubs_command)
    app()
