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

from typer import Argument, Typer

from .commands import add, init, remove, status, use
from .utils import (
    find_prompt_path,
    find_prompt_paths,
    get_prompt_versions,
    get_user_mirascope_settings,
    parse_prompt_file_name,
    prompts_directory_files,
)

app = Typer()

app.command(name="add", help="Add a prompt")(add)
app.command(name="status", help="Check status of prompt(s)")(status)
app.command(name="use", help="Use a prompt")(use)
app.command(name="remove", help="Remove a prompt")(remove)
app.command(name="init", help="Initialize mirascope project")(init)
