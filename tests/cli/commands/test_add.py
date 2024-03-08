"""Test for mirascope cli add command functions."""
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mirascope.cli import app
from mirascope.cli.schemas import MirascopeSettings, VersionTextFile

runner = CliRunner()


def _initialize_tmp_mirascope(tmp_path: Path, golden_prompt: str):
    """Initializes a temporary mirascope directory with the specified prompt."""
    golden_prompt_directory = golden_prompt
    if not golden_prompt.endswith(".py"):
        golden_prompt = f"{golden_prompt}.py"
    source_file = (
        Path(__file__).parent / "golden" / golden_prompt_directory / golden_prompt
    )
    destination_dir_prompts = tmp_path / "prompts"
    destination_dir_prompts.mkdir()
    shutil.copy(source_file, destination_dir_prompts / golden_prompt)
    destination_dir_mirascope_dir = tmp_path / ".mirascope"
    destination_dir_mirascope_dir.mkdir()
    prompt_template_path = (
        Path(__file__).parent.parent.parent.parent
        / "mirascope/cli/generic/prompt_template.j2"
    )
    shutil.copy(
        prompt_template_path, destination_dir_mirascope_dir / "prompt_template.j2"
    )


@pytest.mark.parametrize(
    "version_text_file",
    [
        VersionTextFile(current_revision=None, latest_revision=None),
        # VersionTextFile(current_revision="0001", latest_revision="0001"),
    ],
)
@pytest.mark.parametrize("golden_prompt", ["simple_prompt"])
@pytest.mark.parametrize(
    "mirascope_settings",
    [
        MirascopeSettings(
            mirascope_location=".mirascope",
            auto_tag=True,
            version_file_name="version.txt",
            prompts_location="prompts",
            versions_location=".mirascope/versions",
            format_command="ruff check --select I --fix; ruff format",
        ),
        # MirascopeSettings(
        #     mirascope_location=".mirascope",
        #     auto_tag=False,
        #     version_file_name="version.txt",
        #     prompts_location="prompts",
        #     versions_location=".mirascope/versions",
        #     format_command="ruff check --select I --fix; ruff format",
        # ),
    ],
)
@patch("mirascope.cli.utils.get_user_mirascope_settings")
@patch("mirascope.cli.commands.add.get_user_mirascope_settings")
@patch("mirascope.cli.commands.add.get_prompt_versions")
def test_add(
    mock_get_prompt_versions: MagicMock,
    mock_get_mirascope_settings_add: MagicMock,
    mock_get_mirascope_settings: MagicMock,
    mirascope_settings: MirascopeSettings,
    golden_prompt: str,
    version_text_file: VersionTextFile,
    tmp_path: Path,
):
    """Tests that `add` adds a prompt to the specified version directory."""
    mock_get_mirascope_settings_add.return_value = mirascope_settings
    mock_get_mirascope_settings.return_value = mirascope_settings
    mock_get_prompt_versions.return_value = version_text_file
    current_revision = version_text_file.current_revision
    next_revision = (
        "0001" if current_revision is None else f"{int(current_revision)+1:04d}"
    )
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        if mirascope_settings.auto_tag:
            golden_prompt = f"{golden_prompt}_auto_tag"
        _initialize_tmp_mirascope(Path(td), golden_prompt)
        result = runner.invoke(
            app,
            ["add", golden_prompt],
        )
        assert (
            result.output.strip()
            == f"Adding {mirascope_settings.versions_location}/{golden_prompt}/{next_revision}_{golden_prompt}.py"
        )
        golden_prompt_version_file = f"{next_revision}_{golden_prompt}"
        assert os.path.exists(
            Path(td)
            / mirascope_settings.versions_location
            / golden_prompt
            / f"{next_revision}_{golden_prompt}.py"
        )
        source_file = (
            Path(__file__).parent
            / "golden"
            / golden_prompt
            / f"{golden_prompt_version_file}.py"
        )
        with open(
            Path(td)
            / mirascope_settings.versions_location
            / golden_prompt
            / f"{next_revision}_{golden_prompt}.py",
            "r",
            encoding="utf-8",
        ) as file:
            assert file.read() == source_file.read_text()


@patch("mirascope.cli.commands.add.get_user_mirascope_settings")
def test_add_unknown_file(mock_get_mirascope_settings_add: MagicMock):
    """Tests that `add` fails when the prompt file does not exist."""
    mock_get_mirascope_settings_add.return_value = MirascopeSettings(
        mirascope_location=".mirascope",
        auto_tag=True,
        version_file_name="version.txt",
        prompts_location="prompts",
        versions_location=".mirascope/versions",
    )
    with pytest.raises(FileNotFoundError):
        runner.invoke(app, ["add", "unknown_prompt"], catch_exceptions=False)


@patch("mirascope.cli.commands.add.check_status")
@patch("mirascope.cli.commands.add.get_user_mirascope_settings")
def test_add_no_changes(
    mock_get_mirascope_settings_add: MagicMock,
    mock_check_status: MagicMock,
    tmp_path: Path,
):
    """Tests that `add` does nothing when prompt did not change."""
    mock_check_status.return_value = None
    mock_get_mirascope_settings_add.return_value = MirascopeSettings(
        mirascope_location=".mirascope",
        auto_tag=True,
        version_file_name="version.txt",
        prompts_location="prompts",
        versions_location=".mirascope/versions",
    )
    prompt = "simple_prompt"
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        _initialize_tmp_mirascope(Path(td), prompt)
        result = runner.invoke(app, ["add", prompt])
        assert result.output.strip() == "No changes detected."
