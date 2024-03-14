"""The add command for the Mirascope CLI."""
import os

from typer import Argument

from ..constants import CURRENT_REVISION_KEY, LATEST_REVISION_KEY
from ..enums import MirascopeCommand
from ..schemas import MirascopeCliVariables
from ..utils import (
    check_status,
    get_prompt_versions,
    get_user_mirascope_settings,
    parse_prompt_file_name,
    prompts_directory_files,
    run_format_command,
    update_version_text_file,
    write_prompt_to_template,
)


def add_command(
    prompt_file_name: str = Argument(
        help="Prompt file to add",
        autocompletion=prompts_directory_files,
        parser=parse_prompt_file_name,
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
    auto_tag = mirascope_settings.auto_tag
    # Check status before continuing
    used_prompt_path = check_status(mirascope_settings, prompt_file_name)
    if not used_prompt_path:
        print("No changes detected.")
        return
    prompt_versions_directory = os.path.join(version_directory_path, prompt_file_name)

    # Check if prompt file exists
    if not os.path.exists(f"{prompt_directory_path}/{prompt_file_name}.py"):
        raise FileNotFoundError(
            f"Prompt {prompt_file_name}.py not found in {prompt_directory_path}"
        )
    # Create prompt versions directory if it doesn't exist
    if not os.path.exists(prompt_versions_directory):
        os.makedirs(prompt_versions_directory)
    version_file_path = os.path.join(prompt_versions_directory, version_file_name)
    versions = get_prompt_versions(version_file_path)

    # Open user's prompt file
    user_prompt_file = os.path.join(prompt_directory_path, f"{prompt_file_name}.py")
    with open(user_prompt_file, "r+", encoding="utf-8") as file:
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
            prompt_versions_directory, f"{revision_id}_{prompt_file_name}.py"
        )
        custom_variables = MirascopeCliVariables(
            prev_revision_id=versions.current_revision,
            revision_id=revision_id,
        )
        prompt_file = file.read()

        if auto_tag:
            new_prompt_file = write_prompt_to_template(
                prompt_file, MirascopeCommand.USE, custom_variables
            )
            # Replace contents of user's prompt file with new prompt file with tags
            file.seek(0)
            file.write(new_prompt_file)
            file.truncate()
            # Reset file pointer to beginning of file for revision file read
            file.seek(0)
            run_format_command(user_prompt_file)
        with open(
            revision_file,
            "w+",
            encoding="utf-8",
        ) as file2:
            file2.write(
                write_prompt_to_template(
                    prompt_file, MirascopeCommand.ADD, custom_variables
                )
            )
            keys_to_update = {
                CURRENT_REVISION_KEY: revision_id,
                LATEST_REVISION_KEY: revision_id,
            }
            update_version_text_file(version_file_path, keys_to_update)
    if revision_file:
        run_format_command(revision_file)
    print("Adding " f"{prompt_versions_directory}/{revision_id}_{prompt_file_name}.py")
