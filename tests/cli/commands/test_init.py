"""Test for mirascope cli init command functions."""
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mirascope.cli import app

runner = CliRunner()


@pytest.mark.parametrize(
    "mirascope_location, prompts_location", [(".foo", "bar"), (None, None)]
)
def test_init_command(
    mirascope_location: str,
    prompts_location: str,
    tmp_path: Path,
):
    """Tests that `init` command creates the necessary directories and files."""
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        mirascope_location_args = ["--mirascope-location", mirascope_location]
        prompts_location_args = ["--prompts-location", prompts_location]

        if mirascope_location is None:
            mirascope_location_args = []
            mirascope_location = ".mirascope"

        if prompts_location is None:
            prompts_location_args = []
            prompts_location = "prompts"

        result = runner.invoke(
            app,
            [
                "init",
            ]
            + mirascope_location_args
            + prompts_location_args,
        )
        results = result.output.split("\n")
        assert os.path.exists(f"{td}/{mirascope_location}")
        assert os.path.exists(f"{td}/{mirascope_location}/versions")
        assert os.path.exists(f"{td}/{prompts_location}")
        assert os.path.exists(f"{td}/{prompts_location}/__init__.py")
        assert os.path.exists(f"{td}/mirascope.ini")
        assert os.path.exists(f"{td}/{mirascope_location}/prompt_template.j2")

        assert results[0].strip() == f"Creating {td}/{mirascope_location}/versions"
        assert results[1].strip() == f"Creating {td}/{prompts_location}"
        assert results[2].strip() == f"Creating {td}/{prompts_location}/__init__.py"
        assert results[3].strip() == f"Creating {td}/mirascope.ini"
        assert (
            results[4].strip()
            == f"Creating {td}/{mirascope_location}/prompt_template.j2"
        )
        assert results[5].strip() == "Initialization complete."
        assert result.exit_code == 0
