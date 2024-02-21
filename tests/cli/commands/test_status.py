"""Test for mirascope cli status command functions."""
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mirascope.cli import app
from mirascope.cli.schemas import MirascopeSettings

runner = CliRunner()


def _initialize_tmp_mirascope(tmp_path: Path, golden_prompt: str, golden_version: str):
    """Initializes a temporary mirascope directory with prompt `simple_prompt`."""
    golden_prompt_directory = "simple_prompt"
    if not golden_prompt.endswith(".py"):
        golden_prompt = f"{golden_prompt}.py"
    if not golden_version.endswith(".py"):
        golden_version = f"{golden_version}.py"
    golden_prompt_source_file = (
        Path(__file__).parent / "golden" / golden_prompt_directory / golden_prompt
    )
    destination_dir_prompts = tmp_path / "prompts"
    destination_dir_prompts.mkdir()
    shutil.copy(golden_prompt_source_file, destination_dir_prompts / "simple_prompt.py")
    destination_dir_mirascope_dir = tmp_path / ".mirascope"
    destination_dir_mirascope_dir.mkdir()
    golden_version_source_file = (
        Path(__file__).parent / "golden" / golden_prompt_directory / golden_version
    )
    version_text_file = Path(__file__).parent / "golden" / "version.txt"
    golden_prompts_dir = (
        destination_dir_mirascope_dir / "versions" / golden_prompt_directory
    )
    golden_prompts_dir.mkdir(parents=True)
    shutil.copy(golden_version_source_file, golden_prompts_dir / golden_version)
    shutil.copy(version_text_file, golden_prompts_dir / "version.txt")
    prompt_template_path = (
        Path(__file__).parent.parent.parent.parent
        / "mirascope/cli/generic/prompt_template.j2"
    )
    shutil.copy(
        prompt_template_path, destination_dir_mirascope_dir / "prompt_template.j2"
    )


@pytest.mark.parametrize(
    "golden_prompt", ["simple_prompt", "simple_prompt_with_changes"]
)
@patch("mirascope.cli.commands.status.get_user_mirascope_settings")
def test_status_with_arg(
    mock_get_mirascope_settings_status: MagicMock,
    golden_prompt: str,
    fixture_mirascope_user_settings: MirascopeSettings,
    tmp_path: Path,
):
    """Tests that `status` with arguments returns the correct status."""
    mock_get_mirascope_settings_status.return_value = fixture_mirascope_user_settings
    prompts_location = fixture_mirascope_user_settings.prompts_location
    prompt = "simple_prompt"
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        _initialize_tmp_mirascope(Path(td), golden_prompt, f"0001_{prompt}")
        result = runner.invoke(app, ["status", prompt])
        if golden_prompt == f"{prompt}_with_changes":
            assert (
                result.output.strip()
                == f"Prompt {prompts_location}/{prompt}.py has changed."
            )
        else:
            assert result.output.strip() == "No changes detected."
        assert result.exit_code == 0


@pytest.mark.parametrize(
    "golden_prompt", ["simple_prompt", "simple_prompt_with_changes"]
)
@patch("mirascope.cli.commands.status.get_user_mirascope_settings")
def test_status_no_args(
    mock_get_mirascope_settings_status: MagicMock,
    golden_prompt: str,
    fixture_mirascope_user_settings: MirascopeSettings,
    tmp_path: Path,
):
    """Tests that `status` with no arguments returns the correct status."""
    mock_get_mirascope_settings_status.return_value = fixture_mirascope_user_settings
    prompts_location = fixture_mirascope_user_settings.prompts_location
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        _initialize_tmp_mirascope(Path(td), golden_prompt, "0001_simple_prompt")
        result = runner.invoke(app, ["status"])
        if golden_prompt == "simple_prompt_with_changes":
            results = result.output.splitlines()
            assert results[0].strip() == "The following prompts have changed:"
            assert results[1].strip() == f"{prompts_location}/simple_prompt.py"

        else:
            assert result.output.strip() == "No changes detected."
        assert result.exit_code == 0
