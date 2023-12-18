import argparse
import ast
import glob
import os
from configparser import ConfigParser
from importlib.resources import files
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, Template
from pydantic import BaseModel

from .utils import PythonFileAnalyzer

current_revision = "CURRENT_REVISION"
latest_revision = "LATEST_REVISION"
ignore_variables = {"prev_revision_id", "revision_id"}


def get_user_mirascope_settings():
    """Returns the user's mirascope settings."""
    config = ConfigParser()
    config.read("mirascope.ini")
    return config["mirascope"]


def get_versions(version_file_path: str) -> dict:
    """Returns the current head of the given template."""
    try:
        versions = {}
        with open(version_file_path, "a+", encoding="utf-8") as file:
            file.seek(0)
            for line in file:
                # Check if the current line contains the key
                if line.startswith(current_revision + "="):
                    versions["head"] = line.split("=")[1].strip()
                elif line.startswith(latest_revision + "="):
                    versions["latest"] = line.split("=")[1].strip()
            return versions
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file {version_file_path} was not found.") from e


def check_file_changed(file1_path: str, file2_path: str) -> bool:
    """Checks if the given files have changed."""
    # Parse the first file
    try:
        with open(file1_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file {file1_path} was not found.") from e
    analyzer1 = PythonFileAnalyzer()
    tree1 = ast.parse(content)
    analyzer1.visit(tree1)

    # Parse the second file
    try:
        with open(file2_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file {file2_path} was not found.") from e
    analyzer2 = PythonFileAnalyzer()
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


def find_file_path(directory, prefix):
    """Finds and opens the file with the given prefix in the given directory."""
    pattern = os.path.join(directory, prefix + "*.py")
    prompt_files = glob.glob(pattern)

    if not prompt_files:
        return None  # No files found

    # Return first file found
    return prompt_files[0]


def write_to_template(file: str, command: str, variables: Optional[dict] = None):
    """Writes the given file to the template."""
    mirascope_directory = get_user_mirascope_settings()["mirascope_location"]
    if variables is None:
        variables = {}
    template_loader = FileSystemLoader(
        searchpath=mirascope_directory
    )  # Set your template directory_name
    template_env = Environment(loader=template_loader)
    template = template_env.get_template("prompt_template.j2")
    analyzer = PythonFileAnalyzer()
    tree = ast.parse(file)
    analyzer.visit(tree)
    if command == "add":
        new_variables = variables | analyzer.variables
    elif command == "use":
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


def update_version_text_file(version_file_path: str, updates: dict):
    try:
        modified_lines = []
        edits_made = {
            key: False for key in updates
        }  # Track which updates have been made

        # Read the file and apply updates
        with open(version_file_path, "r", encoding="utf-8") as file:
            for line in file:
                # Check if the current line contains any of the keys
                for key, value in updates.items():
                    if line.startswith(key + "="):
                        modified_lines.append(f"{key}={value}\n")
                        edits_made[key] = True
                        break
                else:  # This else belongs to the for loop
                    modified_lines.append(line)

            # Add any keys that were not found in the file
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


def check_status(mirascope_settings: dict, directory: str):
    version_directory_path = mirascope_settings["versions_location"]
    prompt_directory_path = mirascope_settings["prompts_location"]
    version_file_name = mirascope_settings["version_file_name"]
    prompt_directory = os.path.join(version_directory_path, directory)
    used_prompt_path = f"{prompt_directory_path}/{directory}.py"
    versions = get_versions(f"{prompt_directory}/{version_file_name}")
    current_head = versions["head"] if "head" in versions else None
    if current_head is None:
        return used_prompt_path
    current_version_prompt_path = find_file_path(prompt_directory, current_head)
    has_file_changed = check_file_changed(current_version_prompt_path, used_prompt_path)
    if has_file_changed:
        return used_prompt_path
    return None


def add(args):
    """Adds the given item to the current version."""
    mirascope_settings = get_user_mirascope_settings()
    version_directory_path = mirascope_settings["versions_location"]
    prompt_directory_path = mirascope_settings["prompts_location"]
    version_file_name = mirascope_settings["version_file_name"]
    directory_name: str = args.file
    # Check status before continuing
    used_prompt_path = check_status(mirascope_settings, directory_name)
    if not used_prompt_path:
        print("No changes detected.")
        return
    class_directory = f"{version_directory_path}/{directory_name}"
    version_file_path = f"{class_directory}/{version_file_name}"
    if not os.path.exists(class_directory):
        os.makedirs(class_directory)
    versions = get_versions(version_file_path)
    # Open user's prompt file
    with open(
        f"{prompt_directory_path}/{directory_name}.py", "r+", encoding="utf-8"
    ) as file:
        # Increment revision id
        if "latest" not in versions:
            # first revision
            revision_id = "0001"
        else:
            # default branch with incrementation
            latest_revision_id = versions["latest"]
            revision_id = f"{int(latest_revision_id)+1:04}"
        # Create revision file
        with open(
            f"{class_directory}/{revision_id}_{directory_name}.py",
            "w+",
            encoding="utf-8",
        ) as file2:
            custom_variables = {
                "prev_revision_id": versions["head"] if "head" in versions else None,
                "revision_id": revision_id,
            }
            file2.write(write_to_template(file.read(), "add", custom_variables))
            keys_to_update = {
                current_revision: revision_id,
                latest_revision: revision_id,
            }
            update_version_text_file(version_file_path, keys_to_update)
    print(f"Adding {version_directory_path}/{revision_id}_{directory_name}.py")


def status(args):
    """Checks the status of the current version."""
    mirascope_settings = get_user_mirascope_settings()
    version_directory_path = mirascope_settings["versions_location"]
    directory_name: str = args.file
    if directory_name:
        used_prompt_path = check_status(mirascope_settings, directory_name)
        if used_prompt_path:
            print(f"Prompt {used_prompt_path} has changed.")
        else:
            print("No changes detected.")
    else:
        directores_changed: list[str] = []
        for _, directories, _ in os.walk(version_directory_path):
            for directory in directories:
                used_prompt_path = check_status(mirascope_settings, directory)
                if used_prompt_path:
                    directores_changed.append(used_prompt_path)
        if len(directores_changed) > 0:
            print("The following prompts have changed:")
            for prompt in directores_changed:
                print(f"\t{prompt}".expandtabs(4))
        else:
            print("No changes detected.")


def use(args):
    directory_name = args.directory
    version = args.version
    mirascope_settings = get_user_mirascope_settings()
    used_prompt_path = check_status(mirascope_settings, directory_name)
    if used_prompt_path:
        print("Changes detected, please add or delete changes first.")
        print(f"\tmirascope add {directory_name}".expandtabs(4))
        return
    version_directory_path = mirascope_settings["versions_location"]
    prompt_directory_path = mirascope_settings["prompts_location"]
    version_file_name = mirascope_settings["version_file_name"]
    class_directory = f"{version_directory_path}/{directory_name}"
    revision_file_path = find_file_path(class_directory, version)
    version_file_path = f"{class_directory}/{version_file_name}"
    with open(revision_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    with open(
        f"{prompt_directory_path}/{directory_name}.py", "w+", encoding="utf-8"
    ) as file2:
        file2.write(write_to_template(content, "use"))
    keys_to_update = {
        current_revision: version,
    }
    update_version_text_file(version_file_path, keys_to_update)
    print(f"Using {revision_file_path}")


def init(args):
    """Initializes the mirascope project."""
    destination_dir = Path.cwd()
    directory_name = args.directory
    os.makedirs(f"{directory_name}/versions", exist_ok=True)

    variables = {
        "mirascope_location": "mirascope",
        "versions_location": "versions",
        "prompts_location": "prompts",
        "version_file_name": "version.txt",
    }
    ini_path = files("mirascope.generic").joinpath("mirascope.ini.j2")
    with open(ini_path, "r", encoding="utf-8") as file:
        template = Template(file.read())
        rendered_content = template.render(variables)
        destination_file_path = destination_dir / "mirascope.ini"
        with open(destination_file_path, "w", encoding="utf-8") as destination_file:
            destination_file.write(rendered_content)
    # Create the 'prompt_template.j2' file in the directory specified by user
    prompt_template_path = files("mirascope.generic").joinpath("prompt_template.j2")
    with open(prompt_template_path, "r", encoding="utf-8") as file:
        content = file.read()
    template_path = os.path.join(directory_name, "prompt_template.j2")
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(content)

    print("Initialization complete.")


def main():
    parser = argparse.ArgumentParser(description="CLI Tool")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # Adding 'add' command
    parser_add = subparsers.add_parser("add", help="Add an item")
    parser_add.add_argument("file", help="File to add, without extension (.py)")
    parser_add.set_defaults(func=add)

    # Adding 'status' command
    parser_status = subparsers.add_parser("status", help="Check status of prompts")
    parser_status.add_argument(
        "file", nargs="?", default=None, help="Prompt to check status on"
    )
    parser_status.set_defaults(func=status)

    # Adding 'use' command
    parser_use = subparsers.add_parser("use", help="Use a resource")
    parser_use.add_argument("directory", help="Directory to use")
    parser_use.add_argument("version", help="Version to use")
    parser_use.set_defaults(func=use)

    # Adding 'init' command
    parser_init = subparsers.add_parser("init", help="Initialize mirascope project")
    parser_init.add_argument("directory", help="Main mirascope directory")
    parser_init.set_defaults(func=init)
    # Parse the arguments and call the respective function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
