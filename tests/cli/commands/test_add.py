"""Test for mirascope cli add command functions."""
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mirascope.cli import app
from mirascope.cli.schemas import MirascopeSettings

runner = CliRunner()


def helper(tmp_path: Path):
    source_dir = (
        Path(__file__).parent.parent.parent / "golden" / "cli" / "commands" / "test_add"
    )
    destination_dir_prompts = tmp_path / "prompts"
    source_dir_prompts = source_dir / "prompts"
    destination_dir_mirascope_dir = tmp_path / ".mirascope"
    destination_dir_mirascope_dir.mkdir()
    shutil.copytree(source_dir_prompts, destination_dir_prompts, dirs_exist_ok=True)


# @pytest.mark.parametrize(
#     "golden_prompt", ["prompt1", "prompt2", "prompt3"]
# )
@pytest.mark.parametrize("golden_prompt", ["prompt1"])
@pytest.mark.parametrize(
    "mirascope_settings",
    [
        MirascopeSettings(
            mirascope_location=".mirascope",
            auto_tag=True,
            version_file_name="version.txt",
            prompts_location="prompts",
            versions_location="versions",
        ),
        # MirascopeSettings(
        #     mirascope_location=".mirascope",
        #     auto_tag=False,
        #     version_file_name="version.txt",
        #     prompts_location="prompts",
        #     versions_location="versions",
        # ),
    ],
)
@patch("mirascope.cli.commands.add.get_user_mirascope_settings")
def test_add(
    mock_get_mirascope_settings: MagicMock,
    mirascope_settings: MirascopeSettings,
    golden_prompt: str,
    tmp_path: Path,
):
    """Tests that `add` adds a prompt to the specified version directory."""
    mock_get_mirascope_settings.return_value = mirascope_settings
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        helper(Path(td))
        result = runner.invoke(
            app,
            ["add", golden_prompt],
        )
        print(result.output)
        # with open(
        #     Path(td)
        #     / ".mirascope"
        #     / "versions"
        #     / golden_prompt
        #     / f"0001_{golden_prompt}.py"
        # ) as f:
        #     content = f.read()
        #     print(content)
