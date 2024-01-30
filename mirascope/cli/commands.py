"""The Mirascope CLI prompt management tool.

Typical usage example:

    Initialize the environment:
        $ mirascope init mirascope

    Create a prompt in the prompts directory:
        prompts/my_prompt.py
    
    Add the prompt to create a version:
        $ mirascope add my_prompt

    Iterate on the prompt in the prompts directory:

    Check the status of the prompt:
        $ mirascope status my_prompt

    Add the prompt to create a new version:
        $ mirascope add my_prompt

    Switch between prompts:
        $ mirascope use my_prompt 0001
"""
import os
import subprocess
from importlib.resources import files
from pathlib import Path
from typing import Optional

from jinja2 import Template
from typer import Argument, Option, Typer

from ..enums import MirascopeCommand
from .constants import CURRENT_REVISION_KEY, LATEST_REVISION_KEY
from .schemas import MirascopeSettings
from .utils import (
    check_status,
    find_file_names,
    find_prompt_path,
    get_prompt_versions,
    get_user_mirascope_settings,
    update_version_text_file,
    write_prompt_to_template,
)

app = Typer()


def _prompts_directory_files() -> list[str]:
    """Returns a list of files in the user's prompts directory."""
    mirascope_settings = get_user_mirascope_settings()
    prompt_file_names = find_file_names(mirascope_settings.prompts_location)
    return [f"{name[:-3]}" for name in prompt_file_names]  # remove .py extension


def _parse_prompt_file_name(prompt_file_name: str) -> str:
    """Returns the file name without the .py extension."""
    if prompt_file_name.endswith(".py"):
        return prompt_file_name[:-3]
    return prompt_file_name


@app.command(help="Add a prompt")
def add(
    prompt_file_name: str = Argument(
        help="Prompt file to add",
        autocompletion=_prompts_directory_files,
        parser=_parse_prompt_file_name,
        default="",
    ),
):
    """Adds the given prompt to the specified version directory.

    The contents of the prompt in the user's prompts directory are copied to the version
    directory with the next revision number, and the version file is updated with the
    new revision.

    Args:
        prompt_file_name: The name of the prompt file to add.

    Raises:
        FileNotFoundError: If the file is not found in the specified prompts directory.
    """
    mirascope_settings = get_user_mirascope_settings()
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name

    # Check status before continuing
    used_prompt_path = check_status(mirascope_settings, prompt_file_name)
    if not used_prompt_path:
        print("No changes detected.")
        return
    class_directory = os.path.join(version_directory_path, prompt_file_name)

    # Check if prompt file exists
    if not os.path.exists(f"{prompt_directory_path}/{prompt_file_name}.py"):
        raise FileNotFoundError(
            f"Prompt {prompt_file_name}.py not found in {prompt_directory_path}"
        )
    # Create version directory if it doesn't exist
    if not os.path.exists(class_directory):
        os.makedirs(class_directory)
    version_file_path = os.path.join(class_directory, version_file_name)
    versions = get_prompt_versions(version_file_path)

    # Open user's prompt file
    with open(
        f"{prompt_directory_path}/{prompt_file_name}.py", "r+", encoding="utf-8"
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
        revision_file = os.path.join(
            class_directory, f"{revision_id}_{prompt_file_name}.py"
        )
        with open(
            revision_file,
            "w+",
            encoding="utf-8",
        ) as file2:
            custom_variables = {
                "prev_revision_id": versions.current_revision,
                "revision_id": revision_id,
            }
            file2.write(
                write_prompt_to_template(
                    file.read(), MirascopeCommand.ADD, custom_variables
                )
            )
            keys_to_update = {
                CURRENT_REVISION_KEY: revision_id,
                LATEST_REVISION_KEY: revision_id,
            }
            update_version_text_file(version_file_path, keys_to_update)
    if revision_file:
        if mirascope_settings.format_command:
            format_command: list[str] = mirascope_settings.format_command.split()
            format_command.append(revision_file)
            subprocess.run(
                format_command,
                check=True,
                capture_output=True,
            )
    print(
        "Adding "
        f"{version_directory_path}/{prompt_file_name}/{revision_id}_{prompt_file_name}.py"
    )


@app.command(help="Check status of prompt(s)")
def status(
    prompt_file_name: Optional[str] = Argument(
        help="Prompt to check status on",
        autocompletion=_prompts_directory_files,
        parser=_parse_prompt_file_name,
    ),
) -> None:
    """Checks the status of the current prompt or prompts.

    If a prompt is specified, the status of that prompt is checked. Otherwise, the
    status of all promps are checked. If a prompt has changed, the path to the prompt
    is printed.

    Args:
        prompt_file_name: (Optional) The name of the prompt file to check status on.

    Raises:
        FileNotFoundError: If the file is not found in the specified prompts directory.
    """
    mirascope_settings = get_user_mirascope_settings()
    version_directory_path = mirascope_settings.versions_location

    # If a prompt is specified, check the status of that prompt
    if prompt_file_name:
        used_prompt_path = check_status(mirascope_settings, prompt_file_name)
        if used_prompt_path:
            print(f"Prompt {used_prompt_path} has changed.")
        else:
            print("No changes detected.")
    else:  # Otherwise, check the status of all prompts
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


@app.command(help="Use a prompt")
def use(
    prompt_file_name: str = Argument(
        help="Prompt file to use",
        autocompletion=_prompts_directory_files,
        parser=_parse_prompt_file_name,
    ),
    version: str = Argument(
        help="Version of prompt to use",
    ),
) -> None:
    """Uses the version and prompt specified by the user.

    The contents of the prompt in the versions directory are copied to the user's
    prompts directory, based on the version specified by the user. The version file is
    updated with the new revision.

    Args:
        prompt_file_name: The name of the prompt file to use.
        version: The version of the prompt file to use.

    Raises:
        FileNotFoundError: If the file is not found in the versions directory.
    """
    mirascope_settings = get_user_mirascope_settings()
    used_prompt_path = check_status(mirascope_settings, prompt_file_name)
    # Check status before continuing
    if used_prompt_path:
        print("Changes detected, please add or delete changes first.")
        print(f"\tmirascope add {prompt_file_name}".expandtabs(4))
        return
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name
    class_directory = os.path.join(version_directory_path, prompt_file_name)
    revision_file_path = find_prompt_path(class_directory, version)
    version_file_path = os.path.join(class_directory, version_file_name)
    if revision_file_path is None:
        raise FileNotFoundError(
            f"Prompt version {version} not found in {class_directory}"
        )
    # Open versioned prompt file
    with open(revision_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    # Write to user's prompt file
    prompt_file_path = os.path.join(prompt_directory_path, f"{prompt_file_name}.py")
    with open(prompt_file_path, "w+", encoding="utf-8") as file2:
        file2.write(write_prompt_to_template(content, MirascopeCommand.USE))
    if prompt_file_path:
        if mirascope_settings.format_command:
            format_command: list[str] = mirascope_settings.format_command.split()
            format_command.append(prompt_file_path)
            subprocess.run(
                format_command,
                check=True,
                capture_output=True,
            )

    # Update version file with new current revision
    keys_to_update = {
        CURRENT_REVISION_KEY: version,
    }
    update_version_text_file(version_file_path, keys_to_update)

    print(f"Using {revision_file_path}")


@app.command(help="Initialize mirascope project")
def init(
    mirascope_location: str = Option(
        help="Main mirascope directory", default="mirascope"
    ),
    prompts_location: str = Option(
        help="Location of prompts directory", default="prompts"
    ),
) -> None:
    """Initializes the mirascope project.

    Creates the project structure and files needed for mirascope to work.

    Initial project structure:
    ```
    |
    |-- mirascope.ini
    |-- mirascope
    |   |-- prompt_template.j2
    |   |-- versions/
    |   |   |-- <directory_name>/
    |   |   |   |-- version.txt
    |   |   |   |-- <revision_id>_<directory_name>.py
    |-- prompts/
    ```

    Args:
        mirascope_location: The root mirascope directory to create.
        prompts_location: The user's prompts directory.
    """
    destination_dir = Path.cwd()
    versions_directory = os.path.join(mirascope_location, "versions")
    os.makedirs(versions_directory, exist_ok=True)
    print(f"Creating {destination_dir}/{versions_directory}")
    os.makedirs(prompts_location, exist_ok=True)
    print(f"Creating {destination_dir}/{prompts_location}")
    prompts_init_file: Path = Path(f"{destination_dir}/{prompts_location}/__init__.py")
    if not prompts_init_file.is_file():
        prompts_init_file.touch()
        print(f"Creating {prompts_init_file}")
    # Create the 'mirascope.ini' file in the current directory with some default values
    ini_settings = MirascopeSettings(
        mirascope_location=mirascope_location,
        versions_location="versions",
        prompts_location=prompts_location,
        version_file_name="version.txt",
    )

    # Get templates from the mirascope.cli.generic package
    generic_file_path = files("mirascope.cli.generic")
    ini_path = generic_file_path.joinpath("mirascope.ini.j2")
    with open(str(ini_path), "r", encoding="utf-8") as file:
        template = Template(file.read())
        rendered_content = template.render(ini_settings.model_dump())
        destination_file_path = destination_dir / "mirascope.ini"
        with open(destination_file_path, "w", encoding="utf-8") as destination_file:
            destination_file.write(rendered_content)
            print(f"Creating {destination_file_path}")

    # Create the 'prompt_template.j2' file in the mirascope directory specified by user
    prompt_template_path = generic_file_path.joinpath("prompt_template.j2")
    with open(str(prompt_template_path), "r", encoding="utf-8") as file:
        content = file.read()
    template_path = os.path.join(mirascope_location, "prompt_template.j2")
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(content)
        print(f"Creating {destination_dir}/{template_path}")

    print("Initialization complete.")
