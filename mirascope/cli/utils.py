"""Utility functions for the mirascope library."""
from __future__ import annotations

import ast
import glob
import json
import os
import subprocess
import sys
from configparser import ConfigParser, MissingSectionHeaderError
from pathlib import Path
from typing import Any, Literal, Optional, Union

from jinja2 import Environment, FileSystemLoader

from ..enums import MirascopeCommand
from .constants import CURRENT_REVISION_KEY, LATEST_REVISION_KEY
from .schemas import (
    ClassInfo,
    FunctionInfo,
    MirascopeCliVariables,
    MirascopeSettings,
    VersionTextFile,
)

ignore_variables = {"prev_revision_id", "revision_id"}
mirascope_prompt_bases = (
    "BasePrompt",
    "OpenAICall",
    "GeminiCall",
    "AnthropicCall",
    "WandbOpenAICall",
)


class PromptAnalyzer(ast.NodeVisitor):
    """Utility class for analyzing a Mirascope prompt file.

    The call to `ast.parse()` returns Python code as an AST, whereby each visitor method
    will be called for the corresponding nodes in the AST via `NodeVisitor.visit()`.

    Example:

    ```python
    analyzer = PromptAnalyzer()
    tree = ast.parse(file.read())
    analyzer.visit(tree)
    ```

    """

    def __init__(self) -> None:
        """Initializes the PromptAnalyzer."""
        self.imports: list[tuple[str, Optional[str]]] = []
        self.from_imports: list[tuple[str, str, Optional[str]]] = []
        self.variables: dict[str, Any] = {}
        self.classes: list[ClassInfo] = []
        self.functions: list[FunctionInfo] = []
        self.comments: str = ""

    def visit_Import(self, node) -> None:
        """Extracts imports from the given node."""
        for alias in node.names:
            self.imports.append((alias.name, alias.asname))
        self.generic_visit(node)

    def visit_ImportFrom(self, node) -> None:
        """Extracts from imports from the given node."""
        for alias in node.names:
            self.from_imports.append((node.module, alias.name, alias.asname))
        self.generic_visit(node)

    def visit_Assign(self, node) -> None:
        """Extracts variables from the given node."""
        target = node.targets[0]
        if isinstance(target, ast.Name):
            self.variables[target.id] = ast.unparse(node.value)
        self.generic_visit(node)

    def visit_ClassDef(self, node) -> None:
        """Extracts classes from the given node."""
        class_info = ClassInfo(
            name=node.name,
            bases=[ast.unparse(base) for base in node.bases],
            body="",
            decorators=[ast.unparse(decorator) for decorator in node.decorator_list],
            docstring=None,
        )

        # Extract docstring if present
        docstring = ast.get_docstring(node, False)
        if docstring:
            class_info.docstring = docstring

        # Handle the rest of the class body
        body_nodes = [n for n in node.body if not isinstance(n, ast.Expr)]
        body = []
        for node in body_nodes:
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "prompt_template"
                and isinstance(node.value, ast.Constant)
                and node.end_lineno is not None
                and node.lineno < node.end_lineno
            ):
                # reconstruct template strings to be multi-line
                lines = node.value.s.split("\n")
                body.append(f'{node.targets[0].id} = """{lines.pop(0).strip()}')
                for i, line in enumerate(lines):
                    stripped_line = line.strip()
                    if stripped_line or i < len(lines) - 1:
                        body.append(line.strip())
                body.append('"""')
                body.append("")  # adds final newline
            else:
                body.append(ast.unparse(node))
        class_info.body = "\n".join(body)

        self.classes.append(class_info)

    def visit_AsyncFunctionDef(self, node):
        """Extracts async functions from the given node."""
        return self._visit_Function(node, is_async=True)

    def visit_FunctionDef(self, node):
        """Extracts functions from the given node."""
        return self._visit_Function(node, is_async=False)

    def _visit_Function(self, node, is_async):
        """Extracts functions or async functions from the given node."""
        # Initial function information setup
        function_info = FunctionInfo(
            name=node.name,
            args=[ast.unparse(arg) for arg in node.args.args],
            returns=ast.unparse(node.returns) if node.returns else None,
            body="",
            decorators=[ast.unparse(decorator) for decorator in node.decorator_list],
            docstring=None,
            is_async=is_async,  # Indicates whether the function is async
        )

        # Extract docstring if present
        docstring = ast.get_docstring(node, False)
        if docstring:
            function_info.docstring = docstring

        # Handle the rest of the function body
        body_nodes = [n for n in node.body if not isinstance(n, ast.Expr)]
        function_info.body = "\n".join(ast.unparse(n) for n in body_nodes)

        # Assuming you have a list to store functions
        self.functions.append(function_info)

    def visit_Module(self, node) -> None:
        """Extracts comments from the given node."""
        comments = ast.get_docstring(node, False)
        self.comments = "" if comments is None else comments
        self.generic_visit(node)

    def check_function_changed(self, other: PromptAnalyzer) -> bool:
        """Compares the functions of this file with those of another file."""
        return self._check_definition_changed(other, "function")

    def check_class_changed(self, other: PromptAnalyzer) -> bool:
        """Compares the classes of this file with those of another file."""
        return self._check_definition_changed(other)

    def _check_definition_changed(
        self,
        other: PromptAnalyzer,
        definition_type: Optional[Literal["class", "function"]] = "class",
    ) -> bool:
        """Compares classes or the functions of this file with those of another file"""

        self_definitions: Union[list[ClassInfo], list[FunctionInfo]] = (
            self.classes if definition_type == "class" else self.functions
        )
        other_definitions: Union[list[ClassInfo], list[FunctionInfo]] = (
            other.classes if definition_type == "class" else other.functions
        )

        self_definitions_dict = {
            definition.name: definition for definition in self_definitions
        }
        other_definitions_dict = {
            definition.name: definition for definition in other_definitions
        }

        all_definition_names = set(self_definitions_dict.keys()) | set(
            other_definitions_dict.keys()
        )

        for name in all_definition_names:
            if name in self_definitions_dict and name in other_definitions_dict:
                self_def_dict = self_definitions_dict[name].__dict__
                other_def_dict = other_definitions_dict[name].__dict__
                # Compare attributes of definitions with the same name
                def_diff = {
                    attr: (self_def_dict[attr], other_def_dict[attr])
                    for attr in self_def_dict
                    if self_def_dict[attr] != other_def_dict[attr]
                }
                if def_diff:
                    return True
            else:
                return True

        return False


def get_user_mirascope_settings(
    ini_file_path: str = "mirascope.ini",
) -> MirascopeSettings:
    """Returns the user's mirascope settings.

    Args:
        ini_file_path: The path to the mirascope.ini file.

    Returns:
        The user's mirascope settings as a `MirascopeSettings` instance.

    Raises:
        FileNotFoundError: If the mirascope.ini file is not found.
        KeyError: If the [mirascope] section is missing from the mirascope.ini file.
    """
    config = ConfigParser(allow_no_value=True)
    try:
        read_ok = config.read(ini_file_path)
        if not read_ok:
            raise FileNotFoundError(
                "The mirascope.ini file was not found. Please run "
                "`mirascope init` to create one or run the mirascope CLI from the "
                "same directory as the mirascope.ini file."
            )
        mirascope_config = config["mirascope"]
        return MirascopeSettings(**mirascope_config)
    except MissingSectionHeaderError as e:
        raise MissingSectionHeaderError(ini_file_path, e.lineno, e.source) from e


def prompts_directory_files() -> list[str]:
    """Returns a list of files in the user's prompts directory."""
    mirascope_settings = get_user_mirascope_settings()
    prompt_file_names = find_file_names(mirascope_settings.prompts_location)
    return [f"{name[:-3]}" for name in prompt_file_names]  # remove .py extension


def parse_prompt_file_name(prompt_file_name: str) -> str:
    """Returns the file name without the .py extension."""
    if prompt_file_name.endswith(".py"):
        return prompt_file_name[:-3]
    return prompt_file_name


def get_prompt_versions(version_file_path: str) -> VersionTextFile:
    """Returns the versions of the given prompt.

    Args:
        version_file_path: The path to the prompt.

    Returns:
        A `VersionTextFile` instance with the versions of current and latest revisions.
    """
    versions = VersionTextFile()
    try:
        with open(version_file_path, "r", encoding="utf-8") as file:
            file.seek(0)
            for line in file:
                # Check if the current line contains the key
                if line.startswith(CURRENT_REVISION_KEY + "="):
                    versions.current_revision = line.split("=")[1].strip()
                elif line.startswith(LATEST_REVISION_KEY + "="):
                    versions.latest_revision = line.split("=")[1].strip()
            return versions
    except FileNotFoundError:
        return versions


def check_prompt_changed(file1_path: Optional[str], file2_path: Optional[str]) -> bool:
    """Compare two prompts to check if the given prompts have changed.

    Args:
        file1_path: The path to the first prompt.
        file2_path: The path to the second prompt.

    Returns:
        Whether there are any differences between the two prompts.
    """
    if file1_path is None or file2_path is None:
        raise FileNotFoundError("Prompt or version file is missing.")
    # Parse the first file
    try:
        with open(file1_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file {file1_path} was not found.") from e
    analyzer1 = PromptAnalyzer()
    tree1 = ast.parse(content)
    analyzer1.visit(tree1)

    # Parse the second file
    try:
        with open(file2_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file {file2_path} was not found.") from e
    analyzer2 = PromptAnalyzer()
    tree2 = ast.parse(content)
    analyzer2.visit(tree2)
    # Compare the contents of the two files
    differences = {
        "comments": analyzer1.comments != analyzer2.comments,
        "imports_diff": bool(set(analyzer1.imports) ^ set(analyzer2.imports)),
        "from_imports_diff": bool(
            set(analyzer1.from_imports) ^ set(analyzer2.from_imports)
        ),
        "functions_diff": analyzer1.check_function_changed(analyzer2),
        "variables_diff": set(analyzer1.variables.keys()) - ignore_variables
        ^ set(analyzer2.variables.keys()) - ignore_variables,
        "classes_diff": analyzer1.check_class_changed(analyzer2),
        # Add other comparisons as needed
    }
    return any(differences.values())


def find_file_names(directory: str, prefix: str = "") -> list[str]:
    """Finds all files in a directory.

    Args:
        directory: The directory to search for the prompt.
        prefix: The prefix of the prompt to search for.

    Returns:
        A list of file names found.
    """
    pattern = os.path.join(directory, f"[!_]{prefix}*.py")  # ignores private files
    matching_files_with_dir = glob.glob(pattern)

    # Removing the directory part from each path
    return [os.path.basename(file) for file in matching_files_with_dir]


def find_prompt_paths(directory: Union[Path, str], prefix: str) -> Optional[list[str]]:
    """Finds and opens all prompts with the given directory.

    Args:
        directory: The directory to search for the prompt.
        prefix: The prefix of the prompt to search for.

    Returns:
        A list of paths to the prompt.
    """
    pattern = os.path.join(directory, prefix + "*.py")
    prompt_files = glob.glob(pattern)

    if not prompt_files:
        return None  # No files found

    # Return first file found
    return prompt_files


def find_prompt_path(directory: Union[Path, str], prefix: str) -> Optional[str]:
    """Finds and opens the first found prompt with the given directory.

    Args:
        directory: The directory to search for the prompt.
        prefix: The prefix of the prompt to search for.

    Returns:
        The path to the prompt.
    """
    prompt_files = find_prompt_paths(directory, prefix)
    if prompt_files:
        return prompt_files[0]
    return None


def get_prompt_analyzer(file: str) -> PromptAnalyzer:
    """Gets an instance of PromptAnalyzer for a file

    Args:
        file: The file to analyze

    Returns:
        An instance of PromptAnalyzer
    """
    analyzer = PromptAnalyzer()
    tree = ast.parse(file)
    analyzer.visit(tree)
    return analyzer


def _find_list_from_str(string: str) -> Optional[list[str]]:
    """Finds a list from a string.

    Args:
        string: The string to find the list from.

    Returns:
        The list found from the string.
    """
    start_bracket_index = string.find("[")
    end_bracket_index = string.find("]")
    if (
        start_bracket_index != -1
        and end_bracket_index != -1
        and end_bracket_index > start_bracket_index
    ):
        new_list = string[start_bracket_index : end_bracket_index + 1]
        return json.loads(new_list.replace("'", '"'))
    return None


def _update_tag_decorator_with_version(
    decorators: list[str], variables: MirascopeCliVariables, mirascope_alias: str
) -> Optional[str]:
    """Updates the tag decorator and returns the import name.

    Args:
        decorators: The decorators of the prompt.
        variables: The variables used by mirascope internal.
        mirascope_alias: The alias of the mirascope module.

    Returns:
        The import name of the tag decorator.
    """
    if variables.revision_id is None:
        return None
    import_name = "tags"
    tag_exists = False
    version_tag_prefix = "version:"  # mirascope tag prefix
    version_tag = f"{version_tag_prefix}{variables.revision_id}"
    for index, decorator in enumerate(decorators):
        if any(
            decorator.startswith(prefix)
            for prefix in ("tags(", f"{mirascope_alias}.tags(")
        ):
            tag_exists = True
            import_name = decorator.split("(")[0]
            decorator_arguments = _find_list_from_str(decorator)
            if decorator_arguments is not None:
                if f"{version_tag}" in decorator_arguments:
                    # The version tag already exists
                    break
                elif any(
                    argument.startswith(version_tag_prefix)
                    for argument in decorator_arguments
                ):
                    # Replace the version tag with the current version
                    for i, word in enumerate(decorator_arguments):
                        if word.startswith(version_tag_prefix):
                            decorator_arguments[i] = f"{version_tag}"
                    decorators[index] = f"{import_name}({decorator_arguments})"
                else:
                    # Tag decorator exists, append the current version to the tags
                    decorator_arguments.append(f"{version_tag}")
                    decorators[index] = f"{import_name}({decorator_arguments})"
            else:
                # Add tags decorator
                decorators[index] = f"{import_name}({version_tag})"
            break
    if not tag_exists:
        decorators.append(f'{import_name}(["{version_tag}"])')
    return import_name


def _update_mirascope_imports(imports: list[tuple[str, Optional[str]]]):
    """Updates the mirascope import.

    Args:
        imports: The imports from the PromptAnalyzer class
    """
    if not any(import_name == "mirascope" for import_name, _ in imports):
        imports.append(("mirascope", None))


def _update_mirascope_from_imports(
    member: str, from_imports: list[tuple[str, str, Optional[str]]]
):
    """Updates the mirascope from imports.

    Args:
        member: The member to import.
        from_imports: The from imports from the PromptAnalyzer class
    """
    if not any(
        (
            module_name == "mirascope"
            or module_name == "mirascope.base"
            or module_name == "mirascope.prompts"
        )
        and import_name == member
        for module_name, import_name, _ in from_imports
    ):
        from_imports.append(("mirascope", member, None))


def write_prompt_to_template(
    file: str,
    command: Literal[MirascopeCommand.ADD, MirascopeCommand.USE],
    variables: Optional[MirascopeCliVariables] = None,
) -> str:
    """Writes the given prompt to the template.

    Deconstructs a prompt with ast and reconstructs it using the Jinja2 template, adding
    revision history into the prompt when the command is `MirascopeCommand.ADD`.

    Args:
        file: The path to the prompt.
        command: The CLI command to execute.
        variables: A dictionary of revision ids which are rendered together with
            variable assignments that are not inside any class. Only relevant when
            `command` is `MirascopeCommand.ADD` - if `command` is
            `MirascopeCommand.USE`, `variables` should be `None`.

    Returns:
        The reconstructed prompt.
    """
    mirascope_settings = get_user_mirascope_settings()
    mirascope_directory = mirascope_settings.mirascope_location
    auto_tag = mirascope_settings.auto_tag
    template_loader = FileSystemLoader(searchpath=mirascope_directory)
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("prompt_template.j2")
    analyzer = get_prompt_analyzer(file)
    if variables is None:
        variables = MirascopeCliVariables()

    if command == MirascopeCommand.ADD:
        # double quote revision ids to match how `ast.unparse()` formats strings
        new_variables = {
            k: f"'{v}'" if isinstance(v, str) else None
            for k, v in variables.__dict__.items()
        } | analyzer.variables
    else:  # command == MirascopeCommand.USE
        ignore_variable_keys = dict.fromkeys(ignore_variables, None)
        new_variables = {
            k: analyzer.variables[k]
            for k in analyzer.variables
            if k not in ignore_variable_keys
        }

    if auto_tag:
        import_tag_name: Optional[str] = None
        mirascope_alias = "mirascope"
        for name, alias in analyzer.imports:
            if name == "mirascope" and alias is not None:
                mirascope_alias = alias
                break
        for module, name, alias in analyzer.from_imports:
            if module == "mirascope" and name == "tags" and alias is not None:
                mirascope_alias = alias
                break

        for python_class in analyzer.classes:
            decorators = python_class.decorators
            if python_class.bases and python_class.bases[0] in mirascope_prompt_bases:
                import_tag_name = _update_tag_decorator_with_version(
                    decorators, variables, mirascope_alias
                )

        if import_tag_name == "tags":
            _update_mirascope_from_imports(import_tag_name, analyzer.from_imports)
        elif import_tag_name == f"{mirascope_alias}.tags":
            _update_mirascope_imports(analyzer.imports)

    data = {
        "comments": analyzer.comments,
        "variables": new_variables,
        "imports": analyzer.imports,
        "from_imports": analyzer.from_imports,
        "classes": analyzer.classes,
    }
    return template.render(**data)


def update_version_text_file(
    version_file: str,
    updates: dict[str, str],
) -> None:
    """Updates the version text file.

    Depending on the contents of `updates`, updates the ids of the current and latest
    revisions of the prompt.

    Args:
        version_file: The path to the version text file.
        updates: A dictionary containing updates to the current revision id and/or
            the latest revision id.
    """
    modified_lines = []
    edits_made = {
        key: False for key in updates
    }  # Track which keys already exist in the file
    version_file_path: Path = Path(version_file)
    if not version_file_path.is_file():
        version_file_path.touch()
    # Read the file and apply updates
    with open(version_file_path, "r", encoding="utf-8") as file:
        for line in file:
            # Check if the current line contains any of the keys
            for key, value in updates.items():
                if line.startswith(key + "="):
                    modified_lines.append(f"{key}={value}\n")
                    edits_made[key] = True
                    break
            else:
                # No key found, so keep the line as is
                modified_lines.append(line)

        # Add any keys that were not found at the end of the file
        for key, value in updates.items():
            if not edits_made[key]:
                modified_lines.append(f"{key}={value}\n")

    # Write the modified content back to the file
    with open(version_file_path, "w", encoding="utf-8") as file:
        file.writelines(modified_lines)


def check_status(
    mirascope_settings: MirascopeSettings, directory: str
) -> Optional[str]:
    """Checks the status of the given directory.

    Args:
        mirascope_settings: The user's mirascope settings.
        directory: The name of the prompt file (excluding the .py extension).

    Returns:
        The path to the prompt if the prompt has changed, otherwise `None`.
    """
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name
    prompt_directory = os.path.join(version_directory_path, directory)
    used_prompt_path = f"{prompt_directory_path}/{directory}.py"

    # Get the currently used prompt version
    versions = get_prompt_versions(f"{prompt_directory}/{version_file_name}")
    current_head = versions.current_revision
    if current_head is None:
        return used_prompt_path
    current_version_prompt_path = find_prompt_path(prompt_directory, current_head)
    # Check if users prompt matches the current prompt version
    has_file_changed = check_prompt_changed(
        current_version_prompt_path, used_prompt_path
    )
    if has_file_changed:
        return used_prompt_path
    return None


def run_format_command(file: str) -> None:
    """Runs the format command on the given file.

    Args:
        file: The file to format
    """
    mirascope_settings = get_user_mirascope_settings()
    if mirascope_settings.format_command:
        format_commands: list[list[str]] = [
            command.split() for command in mirascope_settings.format_command.split(";")
        ]
        # assuming the final command takes filename as argument, and as final argument
        format_commands[-1].append(file)
        for command in format_commands:
            subprocess.run(
                [sys.executable, "-m"] + command,
                check=True,
                capture_output=True,
                shell=False,
            )
