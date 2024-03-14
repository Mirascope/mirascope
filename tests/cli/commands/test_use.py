"""Test for mirascope cli use command functions."""
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mirascope.cli import app
from mirascope.cli.schemas import MirascopeSettings

runner = CliRunner()


def _initialize_tmp_mirascope(
    tmp_path: Path, golden_prompt: str, golden_versions: list[str]
):
    """Initializes a temporary mirascope directory with prompt `base_prompt`."""
    golden_prompt_directory = "base_prompt"
    if not golden_prompt.endswith(".py"):
        golden_prompt = f"{golden_prompt}.py"
    golden_versions = [
        f"{golden_version}.py"
        for golden_version in golden_versions
        if not golden_version.endswith(".py")
    ]

    golden_prompt_source_file = (
        Path(__file__).parent / "golden" / golden_prompt_directory / golden_prompt
    )
    destination_dir_prompts = tmp_path / "prompts"
    destination_dir_prompts.mkdir()
    shutil.copy(golden_prompt_source_file, destination_dir_prompts / "base_prompt.py")
    destination_dir_mirascope_dir = tmp_path / ".mirascope"
    destination_dir_mirascope_dir.mkdir()
    golden_prompts_dir = (
        destination_dir_mirascope_dir / "versions" / golden_prompt_directory
    )
    golden_prompts_dir.mkdir(parents=True)
    version_text_file = Path(__file__).parent / "golden" / "version.txt"
    shutil.copy(version_text_file, golden_prompts_dir / "version.txt")
    for golden_version in golden_versions:
        golden_version_source_file = (
            Path(__file__).parent / "golden" / golden_prompt_directory / golden_version
        )
        shutil.copy(golden_version_source_file, golden_prompts_dir / golden_version)
    prompt_template_path = (
        Path(__file__).parent.parent.parent.parent
        / "mirascope/cli/generic/prompt_template.j2"
    )
    shutil.copy(
        prompt_template_path, destination_dir_mirascope_dir / "prompt_template.j2"
    )


@pytest.mark.parametrize("golden_prompt", ["base_prompt"])
@patch("mirascope.cli.utils.get_user_mirascope_settings")
@patch("mirascope.cli.commands.use.get_user_mirascope_settings")
def test_use_command(
    mock_get_mirascope_settings_use: MagicMock,
    mock_get_mirascope_settings: MagicMock,
    golden_prompt: str,
    fixture_mirascope_user_settings: MirascopeSettings,
    tmp_path: Path,
):
    """Tests that `use` command updates the prompt file"""
    mock_get_mirascope_settings_use.return_value = fixture_mirascope_user_settings
    mock_get_mirascope_settings.return_value = fixture_mirascope_user_settings
    prompt = "base_prompt"
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        _initialize_tmp_mirascope(
            Path(td), golden_prompt, [f"0001_{prompt}", f"0002_{prompt}"]
        )
        result = runner.invoke(app, ["use", prompt, "0002"])
        assert result.exit_code == 0


@patch("mirascope.cli.utils.get_user_mirascope_settings")
@patch("mirascope.cli.commands.use.get_user_mirascope_settings")
def test_use_command_file_changed(
    mock_get_mirascope_settings_use: MagicMock,
    mock_get_mirascope_settings: MagicMock,
    fixture_mirascope_user_settings: MirascopeSettings,
    tmp_path: Path,
):
    """Tests that `use` does not update the prompt file if it has changes."""
    mock_get_mirascope_settings_use.return_value = fixture_mirascope_user_settings
    mock_get_mirascope_settings.return_value = fixture_mirascope_user_settings
    prompt = "base_prompt"
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        _initialize_tmp_mirascope(
            Path(td), "base_prompt_with_changes", [f"0001_{prompt}"]
        )
        result = runner.invoke(app, ["use", prompt, "0002"])
        results = result.output.splitlines()
        assert (
            results[0].strip()
            == "Changes detected, please add or remove changes first."
        )
        assert results[1].strip() == f"mirascope add {prompt}"

        assert result.exit_code == 0


@patch("mirascope.cli.utils.get_user_mirascope_settings")
@patch("mirascope.cli.commands.use.get_user_mirascope_settings")
def test_use_no_version_file(
    mock_get_mirascope_settings_use: MagicMock,
    mock_get_mirascope_settings: MagicMock,
    fixture_mirascope_user_settings: MirascopeSettings,
    tmp_path: Path,
):
    """Tests that `use` raises a FileNotFoundError if the version file is not found.

    This test first checks if status has changes, then raises a FileNotFoundError when
    trying to use a version file that does not exist.
    """
    mock_get_mirascope_settings_use.return_value = fixture_mirascope_user_settings
    mock_get_mirascope_settings.return_value = fixture_mirascope_user_settings
    prompt = "base_prompt"
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        _initialize_tmp_mirascope(Path(td), prompt, [f"0001_{prompt}"])
        with pytest.raises(FileNotFoundError):
            runner.invoke(app, ["use", prompt, "0002"], catch_exceptions=False)
