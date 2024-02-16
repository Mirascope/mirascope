"""Test for mirascope cli remove commands functions."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mirascope.cli import app
from mirascope.cli.schemas import MirascopeSettings, VersionTextFile

runner = CliRunner()


@patch("mirascope.cli.commands.remove.get_user_mirascope_settings")
@patch("mirascope.cli.commands.remove.get_prompt_versions")
@patch("mirascope.cli.commands.remove.find_prompt_path")
@patch("mirascope.cli.commands.remove.find_prompt_paths")
@patch("os.remove")
def test_remove(
    mock_remove: MagicMock,
    mock_prompt_paths: MagicMock,
    mock_prompt_path: MagicMock,
    mock_prompt_versions: MagicMock,
    mock_settings: MagicMock,
    fixture_mirascope_user_settings: MirascopeSettings,
    fixture_prompt_versions: VersionTextFile,
    tmp_path: Path,
):
    """Tests that `remove` removes a prompt and detaches any prev_revision_id."""
    version = "0001"
    version2 = "0002"
    version_path = tmp_path / f"{version}_test.py"
    version2_path = tmp_path / f"{version2}_test.py"
    mock_settings.return_value = fixture_mirascope_user_settings
    mock_prompt_versions.return_value = fixture_prompt_versions
    mock_prompt_paths.return_value = [version_path, version2_path]
    mock_prompt_path.return_value = mock_prompt_paths.return_value[0]
    prompt_file_name = "dan"
    version_path.write_text("prev_revision_id = None\n")
    version2_path.write_text(f"prev_revision_id = '{version}'\n")

    result = runner.invoke(app, ["remove", prompt_file_name, version])

    mock_remove.assert_called_once_with(mock_prompt_path.return_value)
    assert (
        result.output.strip()
        == f"Detached {version2_path}\nPrompt {prompt_file_name} {version} "
        "successfully removed"
    )
    assert result.exit_code == 0


@patch("mirascope.cli.commands.remove.get_user_mirascope_settings")
@patch("mirascope.cli.commands.remove.get_prompt_versions")
@patch("mirascope.cli.commands.remove.find_prompt_path")
@patch("mirascope.cli.commands.remove.find_prompt_paths")
@patch("os.remove")
def test_remove_no_prompt_paths(
    mock_remove: MagicMock,
    mock_prompt_paths: MagicMock,
    mock_prompt_path: MagicMock,
    mock_prompt_versions: MagicMock,
    mock_settings: MagicMock,
    fixture_mirascope_user_settings: MirascopeSettings,
    fixture_prompt_versions: VersionTextFile,
    tmp_path: Path,
):
    """Tests that `remove` removes a prompt"""
    version = "0001"
    version_path = tmp_path / f"{version}_test.py"
    mock_settings.return_value = fixture_mirascope_user_settings
    mock_prompt_versions.return_value = fixture_prompt_versions
    mock_prompt_paths.return_value = None
    mock_prompt_path.return_value = version_path
    prompt_file_name = "dan"

    result = runner.invoke(app, ["remove", prompt_file_name, version])

    mock_remove.assert_called_once_with(mock_prompt_path.return_value)
    assert (
        result.output.strip() == f"Prompt {prompt_file_name} {version} "
        "successfully removed"
    )
    assert result.exit_code == 0


@patch("mirascope.cli.commands.remove.get_user_mirascope_settings")
@patch("mirascope.cli.commands.remove.get_prompt_versions")
@patch("os.remove")
def test_remove_current_revision_collision(
    mock_remove: MagicMock,
    mock_prompt_versions: MagicMock,
    mock_settings: MagicMock,
    fixture_mirascope_user_settings: MirascopeSettings,
    fixture_prompt_versions: VersionTextFile,
):
    """Tests that `remove` does not remove a prompt if prompt is active."""
    mock_settings.return_value = fixture_mirascope_user_settings
    mock_prompt_versions.return_value = fixture_prompt_versions
    version: str = (
        fixture_prompt_versions.current_revision
        if fixture_prompt_versions.current_revision
        else ""
    )
    prompt_file_name = "test"
    result = runner.invoke(app, ["remove", prompt_file_name, version])

    assert mock_remove.call_count == 0
    assert (
        result.output.strip()
        == f"Prompt {prompt_file_name} {version} is currently being used. "
        "Please switch to another version first."
    )


@patch("mirascope.cli.commands.remove.get_user_mirascope_settings")
@patch("mirascope.cli.commands.remove.get_prompt_versions")
@patch("mirascope.cli.commands.remove.find_prompt_path")
def test_remove_file_not_found(
    mock_prompt_path: MagicMock,
    mock_prompt_versions: MagicMock,
    mock_settings: MagicMock,
    fixture_mirascope_user_settings: MirascopeSettings,
    fixture_prompt_versions: VersionTextFile,
):
    """Tests that `remove` raises a FileNotFoundError if prompt file is not found."""
    mock_prompt_path.return_value = None
    mock_settings.return_value = fixture_mirascope_user_settings
    mock_prompt_versions.return_value = fixture_prompt_versions

    with pytest.raises(FileNotFoundError):
        result = runner.invoke(app, ["remove", "test", "0001"], catch_exceptions=False)
        assert result.exit_code == 1
