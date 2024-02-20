"""Utility functions for the mirascope library."""
from __future__ import annotations

import ast
import glob
import json
import os
import subprocess
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Literal, Optional, Union

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from ..enums import MirascopeCommand
from .constants import CURRENT_REVISION_KEY, LATEST_REVISION_KEY
from .schemas import MirascopeCliVariables, MirascopeSettings, VersionTextFile

ignore_variables = {"prev_revision_id", "revision_id"}


class ClassInfo(BaseModel):
    name: str
    bases: list[str]
    body: str
    decorators: list[str]
    docstring: Optional[str]


class PromptAnalyzer(ast.NodeVisitor):
    """Utility class for analyzing a Mirascope prompt file.

    Example:

        analyzer = PromptAnalyzer()
        tree = ast.parse(file.read())
        analyzer.visit(tree)

    """

    def __init__(self) -> None:
        """Initializes the PromptAnalyzer."""
        self.imports: list[str] = []
        self.from_imports: list[tuple[str, str]] = []
        self.variables: dict[str, Any] = {}
        self.classes: list[ClassInfo] = []
        self.decorators: list[str] = []
        self.comments: str = ""

    def visit_Import(self, node) -> None:
        """Extracts imports from the given node."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node) -> None:
        """Extracts from imports from the given node."""
        for alias in node.names:
            self.from_imports.append((node.module, alias.name))
        self.generic_visit(node)

    def visit_Assign(self, node) -> None:
        """Extracts variables from the given node."""
        target = node.targets[0]
        if isinstance(target, ast.Name):
            self.variables[target.id] = ast.literal_eval(node.value)
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
        class_info.body = "\n".join(ast.unparse(n) for n in body_nodes)

        self.classes.append(class_info)

    def visit_FunctionDef(self, node) -> None:
        """Extracts decorators from function definitions."""
        for decorator in node.decorator_list:
            self.decorators.append(ast.unparse(decorator))
        self.generic_visit(node)

    def visit_Module(self, node) -> None:
        """Extracts comments from the given node."""
        comments = ast.get_docstring(node, False)
        self.comments = "" if comments is None else comments
        self.generic_visit(node)

    def check_class_changed(self, other: PromptAnalyzer) -> bool:
        """Compares the classes of this file with the classes of another file."""
        self_classes = {c.name: c for c in self.classes}
        other_classes = {c.name: c for c in other.classes}

        all_class_names = set(self_classes.keys()) | set(other_classes.keys())

        for name in all_class_names:
            if name in self_classes and name in other_classes:
                self_class_dict = self_classes[name].__dict__
                other_class_dict = other_classes[name].__dict__
                # Compare attributes of classes with the same name
                class_diff = {
                    attr: (self_class_dict[attr], other_class_dict[attr])
                    for attr in self_class_dict
                    if self_class_dict[attr] != other_class_dict[attr]
                }
                if class_diff:
                    return True
            else:
                return True

        return False


def get_user_mirascope_settings(
    ini_file_path: str = "mirascope.ini",
) -> MirascopeSettings:
    """Returns the user's mirascope settings."""
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
    except KeyError as e:
        raise KeyError(
            "The mirascope.ini file is missing the [mirascope] section."
        ) from e


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
    """Returns the versions of the given prompt."""
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
    """Checks if the given prompts have changed."""
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
        "decorators_diff": bool(set(analyzer1.decorators) ^ set(analyzer2.decorators)),
        "variables_diff": set(analyzer1.variables.keys()) - ignore_variables
        ^ set(analyzer2.variables.keys()) - ignore_variables,
        "classes_diff": analyzer1.check_class_changed(analyzer2),
        # Add other comparisons as needed
    }
    return any(differences.values())


def find_file_names(directory: str, prefix: str = "") -> list[str]:
    """Finds all files in a directory."""
    pattern = os.path.join(directory, "[!_]{prefix}*.py")  # ignores private files
    return glob.glob(pattern)  # Returns all files found


def find_prompt_paths(directory: Union[Path, str], prefix: str) -> Optional[list[str]]:
    """Finds and opens all prompts with the given directory."""
    pattern = os.path.join(directory, prefix + "*.py")
    prompt_files = glob.glob(pattern)

    if not prompt_files:
        return None  # No files found

    # Return first file found
    return prompt_files


def find_prompt_path(directory: Union[Path, str], prefix: str) -> Optional[str]:
    """Finds and opens the first found prompt with the given directory."""
    prompt_files = find_prompt_paths(directory, prefix)
    if prompt_files:
        return prompt_files[0]
    return None


def get_prompt_analyzer(file: str) -> PromptAnalyzer:
    """Gets an instance of PromptAnalyzer for a file"""
    analyzer = PromptAnalyzer()
    tree = ast.parse(file)
    analyzer.visit(tree)
    return analyzer


def _find_list_from_str(string: str) -> Optional[list[str]]:
    """Finds a list from a string."""
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
    decorators: list[str], variables: MirascopeCliVariables
) -> Optional[str]:
    """Updates the tag decorator and returns the import name."""
    if variables.revision_id is None:
        return None
    import_name = "tags"
    tag_exists = False
    version_tag_prefix = "version:"  # mirascope tag prefix
    version_tag = f"{version_tag_prefix}{variables.revision_id}"
    for index, decorator in enumerate(decorators):
        # TODO: Update `mirascope.tags` work with import alias
        if any(decorator.startswith(prefix) for prefix in ("tags(", "mirascope.tags(")):
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


def _update_mirascope_imports(imports: list[str]):
    """Updates the mirascope import."""
    if not any(import_name == "mirascope" for import_name in imports):
        imports.append("mirascope")


def _update_mirascope_from_imports(member: str, from_imports: list[tuple[str, str]]):
    """Updates the mirascope from import."""
    if not any(
        (import_name == "mirascope" or import_name == "mirascope.prompts")
        and alias_name == member
        for import_name, alias_name in from_imports
    ):
        from_imports.append(("mirascope", member))


def write_prompt_to_template(
    file: str,
    command: Literal[MirascopeCommand.ADD, MirascopeCommand.USE],
    variables: Optional[MirascopeCliVariables] = None,
):
    """Writes the given prompt to the template."""
    mirascope_directory = get_user_mirascope_settings().mirascope_location
    template_loader = FileSystemLoader(searchpath=mirascope_directory)
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("prompt_template.j2")
    analyzer = get_prompt_analyzer(file)
    if variables is None:
        variables = MirascopeCliVariables()

    if command == MirascopeCommand.ADD:
        new_variables = variables.__dict__ | analyzer.variables
    else:  # command == MirascopeCommand.USE
        ignore_variable_keys = dict.fromkeys(ignore_variables, None)
        new_variables = {
            k: analyzer.variables[k]
            for k in analyzer.variables
            if k not in ignore_variable_keys
        }

    import_tag_name: Optional[str] = None
    for python_class in analyzer.classes:
        decorators = python_class.decorators
        if python_class.bases and python_class.bases[0] == "Prompt":
            import_tag_name = _update_tag_decorator_with_version(decorators, variables)

    if import_tag_name == "tags":
        _update_mirascope_from_imports(import_tag_name, analyzer.from_imports)
    elif import_tag_name == "mirascope.tags":  # TODO: Update to work with import alias
        _update_mirascope_imports(analyzer.imports)

    data = {
        "comments": analyzer.comments,
        "variables": new_variables,
        "imports": analyzer.imports,
        "from_imports": analyzer.from_imports,
        "classes": analyzer.classes,
    }
    return template.render(**data)


def update_version_text_file(version_file: str, updates: dict):
    """Updates the version text file."""
    try:
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
    except FileNotFoundError:
        print(f"The file {version_file} was not found.")
    except IOError as e:
        print(f"An I/O error occurred: {e}")


def check_status(
    mirascope_settings: MirascopeSettings, directory: str
) -> Optional[str]:
    """Checks the status of the given directory."""
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name
    prompt_directory = os.path.join(version_directory_path, directory)
    used_prompt_path = f"{prompt_directory_path}/{directory}.py"

    # Get the currently used prompt version
    versions = get_prompt_versions(f"{prompt_directory}/{version_file_name}")
    if versions is None:
        return used_prompt_path
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


def run_format_command(file: str):
    """Runs the format command on the given file."""
    mirascope_settings = get_user_mirascope_settings()
    if mirascope_settings.format_command:
        format_command: list[str] = mirascope_settings.format_command.split()
        format_command.append(file)
        subprocess.run(
            format_command,
            check=True,
            capture_output=True,
        )
