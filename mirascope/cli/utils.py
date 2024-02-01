"""Utility functions for the mirascope library."""
import ast
import glob
import os
from configparser import ConfigParser
from pathlib import Path
from typing import Literal, Optional, Union

from jinja2 import Environment, FileSystemLoader

from ..enums import MirascopeCommand
from .constants import CURRENT_REVISION_KEY, LATEST_REVISION_KEY
from .schemas import MirascopeSettings, VersionTextFile

ignore_variables = {"prev_revision_id", "revision_id"}


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
    pattern = f"[!_]{prefix}*.py"  # ignores private files
    return glob.glob(pattern, root_dir=directory)  # Returns all files found


def find_prompt_path(directory: Union[Path, str], prefix: str) -> Optional[str]:
    """Finds and opens the prompt with the given directory."""
    pattern = os.path.join(directory, prefix + "*.py")
    prompt_files = glob.glob(pattern)

    if not prompt_files:
        return None  # No files found

    # Return first file found
    return prompt_files[0]


def write_prompt_to_template(
    file: str,
    command: Literal[MirascopeCommand.ADD, MirascopeCommand.USE],
    variables: Optional[dict] = None,
):
    """Writes the given prompt to the template."""
    mirascope_directory = get_user_mirascope_settings().mirascope_location
    if variables is None:
        variables = {}
    template_loader = FileSystemLoader(searchpath=mirascope_directory)
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("prompt_template.j2")
    analyzer = PromptAnalyzer()
    tree = ast.parse(file)
    analyzer.visit(tree)
    if command == MirascopeCommand.ADD:
        new_variables = variables | analyzer.variables
    else:  # command == MirascopeCommand.USE
        variables = dict.fromkeys(ignore_variables, None)
        new_variables = {
            k: analyzer.variables[k] for k in analyzer.variables if k not in variables
        }

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


class PromptAnalyzer(ast.NodeVisitor):
    """Utility class for analyzing a Mirascope prompt file."""

    def __init__(self):
        """Initializes the PromptAnalyzer."""
        self.imports = []
        self.from_imports = []
        self.variables = {}
        self.classes = []
        self.decorators = []
        self.comments = ""

    def visit_Import(self, node):
        """Extracts imports from the given node."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Extracts from imports from the given node."""
        for alias in node.names:
            self.from_imports.append((node.module, alias.name))
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Extracts variables from the given node."""
        target = node.targets[0]
        if isinstance(target, ast.Name):
            self.variables[target.id] = ast.unparse(node.value)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Extracts classes from the given node."""
        class_info = {
            "name": node.name,
            "bases": [ast.unparse(b) for b in node.bases],
            "body": "",
            "decorators": [ast.unparse(d) for d in node.decorator_list],
            "docstring": None,
        }

        # Extract docstring if present
        docstring = ast.get_docstring(node, False)
        if docstring:
            class_info["docstring"] = docstring

        # Handle the rest of the class body
        body_nodes = [n for n in node.body if not isinstance(n, ast.Expr)]
        class_info["body"] = "\n".join(ast.unparse(n) for n in body_nodes)

        self.classes.append(class_info)

    def visit_FunctionDef(self, node):
        """Extracts decorators from function definitions."""
        for decorator in node.decorator_list:
            self.decorators.append(ast.unparse(decorator))
        self.generic_visit(node)

    def visit_Module(self, node):
        """Extracts comments from the given node."""
        comments = ast.get_docstring(node, False)
        self.comments = "" if comments is None else comments
        self.generic_visit(node)

    def check_class_changed(self, other: "PromptAnalyzer") -> bool:
        """Compares the classes of this file with the classes of another file."""
        self_classes = {c["name"]: c for c in self.classes}
        other_classes = {c["name"]: c for c in other.classes}

        all_class_names = set(self_classes.keys()) | set(other_classes.keys())

        for name in all_class_names:
            if name in self_classes and name in other_classes:
                # Compare attributes of classes with the same name
                class_diff = {
                    attr: (self_classes[name][attr], other_classes[name][attr])
                    for attr in self_classes[name]
                    if self_classes[name][attr] != other_classes[name][attr]
                }
                if class_diff:
                    return True
            else:
                return True

        return False
