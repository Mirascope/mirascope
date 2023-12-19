"""The Mirascope CLI prompt management tool."""
import argparse
import ast
import glob
import os
from configparser import ConfigParser
from importlib.resources import files
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, Template

from .enums import Command
from .models import MirascopeSettings, VersionTextFile
from .utils import _MirascopePromptAnalyzer

CURRENT_REVISION_KEY = "CURRENT_REVISION"
LATEST_REVISION_KEY = "LATEST_REVISION"
ignore_variables = {"prev_revision_id", "revision_id"}

def _get_user_mirascope_settings() -> MirascopeSettings:
    """Returns the user's mirascope settings."""
    config = ConfigParser()
    config.read("mirascope.ini")
    return MirascopeSettings(**config["mirascope"])


def _get_versions(version_file_path: str) -> Optional[VersionTextFile]:
    """Returns the versions of the given prompt."""
    try:
        versions = VersionTextFile()
        with open(version_file_path, "a+", encoding="utf-8") as file:
            file.seek(0)
            for line in file:
                # Check if the current line contains the key
                if line.startswith(CURRENT_REVISION_KEY + "="):
                    versions.current_revision = line.split("=")[1].strip()
                elif line.startswith(LATEST_REVISION_KEY + "="):
                    versions.latest_revision = line.split("=")[1].strip()
            return versions
    except FileNotFoundError:
        return None


def _check_file_changed(file1_path: str, file2_path: str) -> bool:
    """Checks if the given prompts have changed."""
    # Parse the first file
    try:
        with open(file1_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file {file1_path} was not found.") from e
    analyzer1 = _MirascopePromptAnalyzer()
    tree1 = ast.parse(content)
    analyzer1.visit(tree1)

    # Parse the second file
    try:
        with open(file2_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file {file2_path} was not found.") from e
    analyzer2 = _MirascopePromptAnalyzer()
    tree2 = ast.parse(content)
    analyzer2.visit(tree2)
    # Compare the contents of the two files

    differences = {
        "comments": bool(set(analyzer1.comments) ^ set(analyzer2.comments)),
        "imports_diff": bool(set(analyzer1.imports) ^ set(analyzer2.imports)),
        "from_imports_diff": bool(
            set(analyzer1.from_imports) ^ set(analyzer2.from_imports)
        ),
        "variables_diff": bool(
            set(analyzer1.variables.keys())
            ^ set(analyzer2.variables.keys())
            ^ ignore_variables
        ),
        "classes_diff": analyzer1.check_class_changed(analyzer2),
        # Add other comparisons as needed
    }
    return any(differences.values())


def _find_file_path(directory, prefix):
    """Finds and opens the file with the given directory."""
    pattern = os.path.join(directory, prefix + "*.py")
    prompt_files = glob.glob(pattern)

    if not prompt_files:
        return None  # No files found

    # Return first file found
    return prompt_files[0]


def _write_to_template(file: str, command: Command, variables: Optional[dict] = None):
    """Writes the given prompt to the template."""
    mirascope_directory = _get_user_mirascope_settings().mirascope_location
    if variables is None:
        variables = {}
    template_loader = FileSystemLoader(
        searchpath=mirascope_directory
    )  # Set your template directory_name
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("prompt_template.j2")
    analyzer = _MirascopePromptAnalyzer()
    tree = ast.parse(file)
    analyzer.visit(tree)
    if command == Command.ADD:
        new_variables = variables | analyzer.variables
    elif command == Command.USE:
        variables = dict.fromkeys(ignore_variables, None)
        new_variables = analyzer.variables - variables.keys()
    else:
        new_variables = analyzer.variables
    data = {
        "comments": analyzer.comments,
        "variables": new_variables,
        "imports": analyzer.imports,
        "from_imports": analyzer.from_imports,
        "classes": analyzer.classes,
    }
    return template.render(**data)


def _update_version_text_file(version_file_path: str, updates: dict):
    """Updates the version text file."""
    try:
        modified_lines = []
        edits_made = {
            key: False for key in updates
        }  # Track which keys already exist in the file

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
        print(f"The file {version_file_path} was not found.")
    except IOError as e:
        print(f"An I/O error occurred: {e}")


def _check_status(mirascope_settings: MirascopeSettings, directory: str) -> Optional[str]:
    """Checks the status of the given directory."""
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name
    prompt_directory = os.path.join(version_directory_path, directory)
    used_prompt_path = f"{prompt_directory_path}/{directory}.py"
    # Get the currently used prompt version
    versions = _get_versions(f"{prompt_directory}/{version_file_name}")
    if versions is None:
        return used_prompt_path
    current_head = versions.current_revision
    if current_head is None:
        return used_prompt_path
    current_version_prompt_path = _find_file_path(prompt_directory, current_head)
    # Check if users prompt matches the current prompt version
    has_file_changed = _check_file_changed(current_version_prompt_path, used_prompt_path)
    if has_file_changed:
        return used_prompt_path
    return None


def _add(args):
    """Adds the given prompt to the specified version directory.

    The contents of the prompt in the users prompts directory are copied to the version directory
    with the next revision number, and the version file is updated with the new revision.

    Typical Usage Example:

        mirascope add <directory_name>

    Args:
        args: The directory name passed to the add command.
    Returns:
        None
    Raises:
        FileNotFoundError: If the file is not found in the specified prompts directory.
    """
    mirascope_settings = _get_user_mirascope_settings()
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name
    directory_name: str = args.file
    # Check status before continuing
    used_prompt_path = _check_status(mirascope_settings, directory_name)
    if not used_prompt_path:
        print("No changes detected.")
        return
    class_directory = os.path.join(version_directory_path, directory_name)
    version_file_path = os.path.join(class_directory, version_file_name)
    if not os.path.exists(class_directory):
        os.makedirs(class_directory)
    versions = _get_versions(version_file_path)
    # Open user's prompt file
    with open(
        f"{prompt_directory_path}/{directory_name}.py", "r+", encoding="utf-8"
    ) as file:
        # Increment revision id
        if versions.latest_revision is None:
            # first revision
            revision_id = "0001"
        else:
            # default branch with incrementation
            latest_revision_id = versions.latest_revision
            revision_id = f"{int(latest_revision_id)+1:04}"
        # Create revision file
        with open(
            f"{class_directory}/{revision_id}_{directory_name}.py",
            "w+",
            encoding="utf-8",
        ) as file2:
            custom_variables = {
                "prev_revision_id": versions.current_revision,
                "revision_id": revision_id,
            }
            file2.write(_write_to_template(file.read(), Command.ADD, custom_variables))
            keys_to_update = {
                CURRENT_REVISION_KEY: revision_id,
                LATEST_REVISION_KEY: revision_id,
            }
            _update_version_text_file(version_file_path, keys_to_update)
    print(f"Adding {version_directory_path}/{revision_id}_{directory_name}.py")


def _status(args):
    """
    Checks the status of the current prompt or prompts.

    If a prompt is specified, the status of that prompt is checked. Otherwise, the status of all
    promps are checked. If a prompt has changed, the path to the prompt is printed.

    Typical Usage Example:
            
        mirascope status <directory_name>
        or
        mirascope status

    Args:
        args: The directory name (optional) passed to the status command.
    Returns:
        None
    Raises:
        FileNotFoundError: If the file is not found in the specified prompts directory.

    """
    mirascope_settings = _get_user_mirascope_settings()
    version_directory_path = mirascope_settings.versions_location
    directory_name: str = args.file
    # If a prompt is specified, check the status of that prompt
    if directory_name:
        used_prompt_path = _check_status(mirascope_settings, directory_name)
        if used_prompt_path:
            print(f"Prompt {used_prompt_path} has changed.")
        else:
            print("No changes detected.")
    else:
        directores_changed: list[str] = []
        # Otherwise, check the status of all prompts
        for _, directories, _ in os.walk(version_directory_path):
            for directory in directories:
                used_prompt_path = _check_status(mirascope_settings, directory)
                if used_prompt_path:
                    directores_changed.append(used_prompt_path)
        if len(directores_changed) > 0:
            print("The following prompts have changed:")
            for prompt in directores_changed:
                print(f"\t{prompt}".expandtabs(4))
        else:
            print("No changes detected.")


def _use(args):
    """
    Uses the version and prompt specified by the user.

    The contents of the prompt in the version directory are copied to the users prompts directory,
    based on the version specified by the user. The version file is updated with the new revision.

    Typical Usage Example:
    
            mirascope use <prompt_directory> <version>
    Args:
        args: The prompt_directory name and version passed to the use command.
    Returns:
        None
    Raises:
        FileNotFoundError: If the file is not found in the specified prompts directory.
    """
    directory_name = args.prompt_directory
    version = args.version
    mirascope_settings = _get_user_mirascope_settings()
    used_prompt_path = _check_status(mirascope_settings, directory_name)
    # Check status before continuing
    if used_prompt_path:
        print("Changes detected, please add or delete changes first.")
        print(f"\tmirascope add {directory_name}".expandtabs(4))
        return
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name
    class_directory = os.path.join(version_directory_path, directory_name)
    revision_file_path = _find_file_path(class_directory, version)
    version_file_path = os.path.join(class_directory, version_file_name)
    # Open versioned prompt file
    with open(revision_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    prompt_file_name = os.path.join(prompt_directory_path, f"{directory_name}.py")
    # Write to user's prompt file
    with open(prompt_file_name, "w+", encoding="utf-8") as file2:
        file2.write(_write_to_template(content, Command.USE))
    # Update version file with new current revision
    keys_to_update = {
        CURRENT_REVISION_KEY: version,
    }
    _update_version_text_file(version_file_path, keys_to_update)
    print(f"Using {revision_file_path}")


def _init(args):
    """
    Initializes the mirascope project.

    Creates the project structure and files needed for mirascope to work.

    Sample project structure:
    |
    |-- mirascope.ini
    |-- mirascope
    |   |-- prompt_template.j2
    |   |-- versions/
    |   |   |-- <directory_name>/
    |   |   |   |-- version.txt
    |   |   |   |-- <revision_id>_<directory_name>.py
    |-- prompts/

    Typical Usage Example:
        
        mirascope init mirascope

    Args:
        args: The mirascope directory name passed to the init command.
    Returns:
        None
    """
    destination_dir = Path.cwd()
    directory_name = args.directory
    versions_directory = os.path.join(directory_name, "versions")
    os.makedirs(versions_directory, exist_ok=True)
    print(f"Creating {versions_directory}")
    # Create the 'mirascope.ini' file in the current directory with some default values
    ini_settings = MirascopeSettings(
        mirascope_location="mirascope",
        versions_location="versions",
        prompts_location="prompts",
        version_file_name="version.txt",
    )
    ini_path = files("mirascope.generic").joinpath("mirascope.ini.j2")
    with open(ini_path, "r", encoding="utf-8") as file:
        template = Template(file.read())
        rendered_content = template.render(ini_settings.model_dump())
        destination_file_path = destination_dir / "mirascope.ini"
        with open(destination_file_path, "w", encoding="utf-8") as destination_file:
            destination_file.write(rendered_content)
            print(f"Creating {destination_file_path}")
    # Create the 'prompt_template.j2' file in the mirascope directory specified by user
    prompt_template_path = files("mirascope.generic").joinpath("prompt_template.j2")
    with open(prompt_template_path, "r", encoding="utf-8") as file:
        content = file.read()
    template_path = os.path.join(directory_name, "prompt_template.j2")
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(content)
        print(f"Creating {template_path}")

    print("Initialization complete.")


def main():
    """The runner for Mirascope CLI tool"""
    parser = argparse.ArgumentParser(description="Mirascope CLI Tool")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # Adding 'add' command
    parser_add = subparsers.add_parser("add", help="Add an item")
    parser_add.add_argument("file", help="File to add, without extension (.py)")
    parser_add.set_defaults(func=_add)

    # Adding 'status' command
    parser_status = subparsers.add_parser("status", help="Check status of prompts")
    parser_status.add_argument(
        "file", nargs="?", default=None, help="Prompt to check status on"
    )
    parser_status.set_defaults(func=_status)

    # Adding 'use' command
    parser_use = subparsers.add_parser("use", help="Use a prompt")
    parser_use.add_argument("prompt_directory", help="Prompt directory to use")
    parser_use.add_argument("version", help="Version of prompt to use")
    parser_use.set_defaults(func=_use)

    # Adding 'init' command
    parser_init = subparsers.add_parser("init", help="Initialize mirascope project")
    parser_init.add_argument("directory", help="Main mirascope directory")
    parser_init.set_defaults(func=_init)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
