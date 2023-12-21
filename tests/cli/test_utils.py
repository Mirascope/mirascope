from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, Mock, patch

import pytest
from jinja2 import Environment
from pydantic import ValidationError

from mirascope.cli.constants import CURRENT_REVISION_KEY, LATEST_REVISION_KEY
from mirascope.cli.pydantic_models import MirascopeSettings
from mirascope.cli.utils import (
    check_prompt_changed,
    find_prompt_path,
    get_prompt_versions,
    get_user_mirascope_settings,
    write_prompt_to_template,
)
from mirascope.enums import MirascopeCommand


def _get_mirascope_ini() -> str:
    """Get the contents of the mirascope.ini.j2 file"""
    mirascope_ini_path = Path("mirascope/cli/generic/mirascope.ini.j2")
    return mirascope_ini_path.read_text(encoding="utf-8")


def test_valid_mirascope_settings(tmp_path: Path):
    """Tests that the ini file properly maps to pydantic model"""
    mirascope_ini = _get_mirascope_ini()
    ini_path = tmp_path / "settings.ini"
    ini_path.write_text(mirascope_ini)
    settings = get_user_mirascope_settings(str(ini_path))
    assert isinstance(settings, MirascopeSettings)


def test_invalid_mirascope_settings(tmp_path: Path):
    """Tests that an invalid ini file raises pydantic ValidationError"""
    mirascope_ini = _get_mirascope_ini()
    additional_settings = "invalid_setting = 1"
    invalid_mirascope_ini = mirascope_ini + "\n" + additional_settings
    ini_path = tmp_path / "settings.ini"
    ini_path.write_text(invalid_mirascope_ini)
    """Tests that an invalid ini file raises pydantic ValidationError"""
    with pytest.raises(ValidationError):
        get_user_mirascope_settings(str(ini_path))


def _write_version_text_file(tmp_path: Path):
    """Writes a version.txt file to the temporary directory"""
    content = dedent(
        f"""
    {CURRENT_REVISION_KEY}=0002
    {LATEST_REVISION_KEY}=0003
    """
    )
    file_path = tmp_path / "version.txt"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def test_get_prompt_version(tmp_path: Path):
    """Tests that the version.txt file is properly read"""
    versions = get_prompt_versions(_write_version_text_file(tmp_path))
    assert versions.current_revision == "0002"
    assert versions.latest_revision == "0003"


def test_get_invalid_path_prompt_version():
    """Tests that missing version.txt version is properly handled"""
    versions = get_prompt_versions("invalid_path")
    assert versions.current_revision is None
    assert versions.latest_revision is None


def _write_python_prompt_file(tmp_path: Path, directory_name: str, content: str):
    """Returns the contents of a python prompt file"""
    file_name = f"{directory_name}.py"
    file_path = tmp_path / file_name
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def test_find_prompt_path(tmp_path: Path):
    """Tests that the prompt path is properly found given only a prefix"""
    version = "0001"
    directory_name = f"{version}_my_prompt"
    content = dedent(
        """
    print('Hello World!)
    """
    )
    prompt_path = _write_python_prompt_file(tmp_path, directory_name, content)
    found_prompt_path = find_prompt_path(tmp_path, version)
    assert prompt_path == found_prompt_path


@pytest.mark.parametrize(
    "first_content, second_content",
    [
        # imports
        (
            dedent(
                """
                import bar
                """
            ),
            dedent(
                """
                import foo
                """
            ),
        ),
        # from_imports
        (
            dedent(
                """
                from bar import foo
                """
            ),
            dedent(
                """
                from foo import bar
                """
            ),
        ),
        # variables
        (
            dedent(
                """
                foo = 'bar'
                """
            ),
            dedent(
                """
                baz = 'qux'
                """
            ),
        ),
        # classes
        (
            dedent(
                """
                class Bar(Foo):
                    foo = 'bar'
                """
            ),
            dedent(
                """
                class Bar(Foo):
                    foo = 'baz'
                """
            ),
        ),
        # comments
        (
            dedent(
                '''
                """This is a comment"""
                '''
            ),
            dedent(
                '''
                """This is a different comment"""
                '''
            ),
        ),
    ],
)
def test_check_prompt_changed_import(
    tmp_path: Path, first_content: str, second_content: str
):
    """Tests that the prompt is properly detected as changed given different content"""
    directory_name = "my_prompt"
    first_version_path = _write_python_prompt_file(
        tmp_path, f"0001_{directory_name}", first_content
    )
    second_version_path = _write_python_prompt_file(
        tmp_path, f"0002_{directory_name}", second_content
    )
    assert check_prompt_changed(first_version_path, second_version_path)


@pytest.mark.parametrize(
    "command, expected_variables",
    [
        (MirascopeCommand.ADD, {"prev_revision_id": "0001", "revision_id": "0002"}),
        (MirascopeCommand.USE, None),
    ],
)
@patch("mirascope.cli.utils.get_user_mirascope_settings")
@patch.object(Environment, "get_template")
def test_write_prompt_to_template(
    mock_get_template: Mock,
    mock_settings: Mock,
    command: MirascopeCommand,
    expected_variables: dict,
):
    """Tests that a prompt is properly created from the template"""

    sample_file_content = dedent(
        '''
    """This is a comment"""
    foo = bar
    '''
    )

    sample_directory = "/mock/directory"
    mock_settings.return_value.location = sample_directory

    mock_template = MagicMock()
    sample_template_content = "Template with {{ variables }} and {{ comments }}"
    mock_template.render.return_value = sample_template_content
    mock_get_template.return_value = mock_template

    write_prompt_to_template(sample_file_content, command, expected_variables)

    mock_settings.assert_called_once()
    mock_get_template.assert_called_with("prompt_template.j2")

    assert mock_template.render.call_args is not None
