"""Fixtures for CLI tests."""
import pytest

from mirascope.cli.schemas import MirascopeSettings, VersionTextFile


@pytest.fixture()
def fixture_mirascope_user_settings() -> MirascopeSettings:
    """Returns a `MirascopeSettings` instance."""
    return MirascopeSettings(
        format_command="ruff check --select I --fix; ruff format",
        mirascope_location=".mirascope",
        prompts_location="prompts",
        version_file_name="version.txt",
        versions_location=".mirascope/versions",
        auto_tag=True,
    )


@pytest.fixture
def fixture_prompt_versions() -> VersionTextFile:
    """Returns a `VersionTextFile` instance."""
    return VersionTextFile(current_revision="0002", latest_revision="0002")
