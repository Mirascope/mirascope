"""The use command for the Mirascope CLI."""
import os

from typer import Argument

from ..constants import CURRENT_REVISION_KEY
from ..enums import MirascopeCommand
from ..utils import (
    check_status,
    find_prompt_path,
    get_user_mirascope_settings,
    parse_prompt_file_name,
    prompts_directory_files,
    run_format_command,
    update_version_text_file,
    write_prompt_to_template,
)


def use_command(
    prompt_file_name: str = Argument(
        help="Prompt file to use",
        autocompletion=prompts_directory_files,
        parser=parse_prompt_file_name,
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
        print("Changes detected, please add or remove changes first.")
        print(f"\tmirascope add {prompt_file_name}".expandtabs(4))
        return
    version_directory_path = mirascope_settings.versions_location
    prompt_directory_path = mirascope_settings.prompts_location
    version_file_name = mirascope_settings.version_file_name
    prompt_versions_directory = os.path.join(version_directory_path, prompt_file_name)
    revision_file_path = find_prompt_path(prompt_versions_directory, version)
    version_file_path = os.path.join(prompt_versions_directory, version_file_name)
    if revision_file_path is None:
        raise FileNotFoundError(
            f"Prompt version {version} not found in {prompt_versions_directory}"
        )
    # Open versioned prompt file
    with open(revision_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    # Write to user's prompt file
    prompt_file_path = os.path.join(prompt_directory_path, f"{prompt_file_name}.py")
    with open(prompt_file_path, "w+", encoding="utf-8") as file2:
        file2.write(write_prompt_to_template(content, MirascopeCommand.USE))
    if prompt_file_path:
        run_format_command(prompt_file_path)

    # Update version file with new current revision
    keys_to_update = {
        CURRENT_REVISION_KEY: version,
    }
    update_version_text_file(version_file_path, keys_to_update)

    print(f"Using {revision_file_path}")
