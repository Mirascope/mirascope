"""The init command for the Mirascope CLI."""
import os
from importlib.resources import files
from pathlib import Path

from jinja2 import Template
from typer import Option

from ..schemas import MirascopeSettings


def init_command(
    mirascope_location: str = Option(
        help="Main mirascope directory", default=".mirascope"
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
    |-- .mirascope
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
        auto_tag=True,
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
