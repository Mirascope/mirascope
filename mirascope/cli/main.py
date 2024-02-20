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


from typer import Typer

from .commands import (
    add_command,
    init_command,
    remove_command,
    status_command,
    use_command,
)

app = Typer()

app.command(name="add", help="Add a prompt")(add_command)
app.command(name="status", help="Check status of prompt(s)")(status_command)
app.command(name="use", help="Use a prompt")(use_command)
app.command(name="remove", help="Remove a prompt")(remove_command)
app.command(name="init", help="Initialize mirascope project")(init_command)
