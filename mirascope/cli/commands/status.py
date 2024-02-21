"""The status command for the Mirascope CLI."""
import os
from typing import Optional

from typer import Argument

from ..utils import (
    check_status,
    get_user_mirascope_settings,
    parse_prompt_file_name,
    prompts_directory_files,
)


def status_command(
    prompt_file_name: Optional[str] = Argument(
        help="Prompt to check status on",
        autocompletion=prompts_directory_files,
        parser=parse_prompt_file_name,
        default=None,
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
