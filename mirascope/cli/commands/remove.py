"""The remove command for the Mirascope CLI."""
import os

from typer import Argument

from ..utils import (
    find_prompt_path,
    find_prompt_paths,
    get_prompt_versions,
    get_user_mirascope_settings,
    parse_prompt_file_name,
    prompts_directory_files,
)


def remove_command(
    prompt_file_name: str = Argument(
        help="Prompt file to remove",
        autocompletion=prompts_directory_files,
        parser=parse_prompt_file_name,
        default="",
    ),
    version: str = Argument(
        help="Version of prompt to use",
    ),
):
    """Removes the version from the versions directory

    All versions with prev_revision_id matching the deleted version are detached.

    Args:
        prompt_file_name: The name of the prompt file to remove.
        version: The version of the prompt to remove

    Raises:
        FileNotFoundError: If the file is not found in the specified prompts or
          versions directory.
    """
    mirascope_settings = get_user_mirascope_settings()
    version_directory_path = mirascope_settings.versions_location
    version_file_name = mirascope_settings.version_file_name
    prompt_versions_directory = os.path.join(version_directory_path, prompt_file_name)
    version_file_path = os.path.join(prompt_versions_directory, version_file_name)

    revisions = get_prompt_versions(version_file_path)
    if revisions.current_revision == version:
        print(
            f"Prompt {prompt_file_name} {version} is currently being used. "
            "Please switch to another version first."
        )
        return

    revision_file_path = find_prompt_path(prompt_versions_directory, version)
    if not revision_file_path:
        raise FileNotFoundError(
            f"Prompt version {version} not found in {prompt_versions_directory}"
        )
    # TODO: Implement rollback in case of failure
    os.remove(revision_file_path)

    # Detach any revisions that had the deleted version as their prev_revision_id
    revision_file_paths = find_prompt_paths(prompt_versions_directory, "")
    if revision_file_paths is None:
        revision_file_paths = []
    for revision_file_path in revision_file_paths:
        prev_revision_id_found = False
        with open(
            revision_file_path,
            "r",
            encoding="utf-8",
        ) as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if "prev_revision_id" in line:
                    current_prev_revision_id = line.strip().split("=")[1].strip()
                    current_prev_revision_id = current_prev_revision_id[1:-1]
                    if current_prev_revision_id == version:
                        lines[i] = "prev_revision_id = None\n"
                        prev_revision_id_found = True
                    break
        if prev_revision_id_found:
            with open(revision_file_path, "w", encoding="utf-8") as file:
                file.writelines(lines)
            print(f"Detached {revision_file_path}")
    print(f"Prompt {prompt_file_name} {version} successfully removed")
