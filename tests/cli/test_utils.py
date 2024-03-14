"""Test for mirascope cli utility functions."""
import os
from configparser import MissingSectionHeaderError
from pathlib import Path
from textwrap import dedent
from typing import Literal, Optional
from unittest.mock import MagicMock, patch

import pytest
from jinja2 import Environment
from pydantic import ValidationError

from mirascope.cli.constants import CURRENT_REVISION_KEY, LATEST_REVISION_KEY
from mirascope.cli.enums import MirascopeCommand
from mirascope.cli.schemas import (
    ClassInfo,
    FunctionInfo,
    MirascopeCliVariables,
    MirascopeSettings,
)
from mirascope.cli.utils import (
    PromptAnalyzer,
    check_prompt_changed,
    find_file_names,
    find_prompt_path,
    get_prompt_analyzer,
    get_prompt_versions,
    get_user_mirascope_settings,
    parse_prompt_file_name,
    prompts_directory_files,
    write_prompt_to_template,
)


def _get_mirascope_ini() -> str:
    """Get the contents of the mirascope.ini.j2 file"""
    mirascope_ini_path = Path("mirascope/cli/generic/mirascope.ini.j2")
    return mirascope_ini_path.read_text(encoding="utf-8")


def _get_prompt_template() -> str:
    """Get the contents of the prompt_template.j2 file"""
    prompt_template_path = Path("mirascope/cli/generic/prompt_template.j2")
    return prompt_template_path.read_text(encoding="utf-8")


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
    ini_path_no_section = tmp_path / "bad_settings.ini"
    ini_path_no_section.write_text('invalid_settings = "no [mirascope] section"s')
    with pytest.raises(FileNotFoundError):
        get_user_mirascope_settings("invalid_path")
    with pytest.raises(ValidationError):
        get_user_mirascope_settings(str(ini_path))
    with pytest.raises(MissingSectionHeaderError):
        get_user_mirascope_settings(str(ini_path_no_section))


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


def test_get_prompt_versions(tmp_path: Path):
    """Tests that the version.txt file is properly read"""
    versions = get_prompt_versions(_write_version_text_file(tmp_path))
    assert versions.current_revision == "0002"
    assert versions.latest_revision == "0003"


def test_get_invalid_path_prompt_versions():
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


def test_check_prompt_changed_errors(tmp_path: Path):
    directory_name = "my_prompt"
    first_version_path = _write_python_prompt_file(
        tmp_path, f"0001_{directory_name}", ""
    )
    second_version_path = _write_python_prompt_file(
        tmp_path, f"0002_{directory_name}", ""
    )
    with pytest.raises(FileNotFoundError):
        check_prompt_changed(first_version_path, "invalid_path2")
    with pytest.raises(FileNotFoundError):
        check_prompt_changed("invalid_path1", second_version_path)
    with pytest.raises(FileNotFoundError):
        check_prompt_changed(None, None)


def test_get_prompt_analyzer():
    """Tests that a prompt is properly created from the template"""

    sample_file_content = dedent(
        '''
        """This is a comment"""
        from fastapi import FastAPI

        app = FastAPI()
        foo = "bar"
        number = 1
        a_list = [1, 2, 3]

        @app.get("/")
        async def root() -> dict[str, str]:
            """This is root"""
            return {"message": "Hello World"}

        def a_function(foo: str, bar: int) -> None:
            pass

        '''
    )
    analyzer = get_prompt_analyzer(sample_file_content)
    assert analyzer.comments == "This is a comment"
    assert analyzer.from_imports == [("fastapi", "FastAPI", None)]
    assert analyzer.variables == {
        "foo": "'bar'",
        "number": "1",
        "a_list": "[1, 2, 3]",
        "app": "FastAPI()",
    }
    assert analyzer.functions[0] == FunctionInfo(
        name="root",
        docstring="This is root",
        args=[],
        body="return {'message': 'Hello World'}",
        decorators=["app.get('/')"],
        returns="dict[str, str]",
        is_async=True,
    )
    assert analyzer.functions[1] == FunctionInfo(
        name="a_function",
        docstring=None,
        args=["foo: str", "bar: int"],
        body="pass",
        decorators=[],
        returns="None",
        is_async=False,
    )


def test_prompt_analyzer_definition_changed():
    sample_file_content1 = dedent(
        '''
        """This is a comment"""

        def a_function(foo: str, bar: int) -> None:
            pass
        '''
    )
    sample_file_content2 = dedent(
        '''
        """This is a comment"""

        def b_function(foo: str, bar: int) -> None:
            pass
        '''
    )
    analyzer1 = get_prompt_analyzer(sample_file_content1)
    analyzer2 = get_prompt_analyzer(sample_file_content2)
    assert analyzer1.check_function_changed(analyzer2)


@pytest.mark.parametrize(
    "from_imports",
    [
        [],
        [("mirascope", "tags", "mirascope_tag")],
        [("mirascope", "tags", None)],
    ],
)
@pytest.mark.parametrize(
    "imports",
    [
        [],
        [("mirascope", None)],
        [("mirascope", "ms")],
        [("mirascope", "Mirascope"), ("fastapi", "FastAPI")],
    ],
)
@pytest.mark.parametrize(
    "class_decorators",
    [
        ["tags(['movie_project'])"],  # no version
        ["tags(['version:0001', 'movie_project'])"],  # version first
        ["tags(['movie_project', 'version:0001'])"],  # different version
        ["tags(['movie_project', 'version:0002'])"],  # same as revision_id
        ["tags(['movie_project', 'version:0002', 'another_tag'])"],  # tag in middle
        [""],  # no tags
        ["tags(['version:0001', 'version:0002'])"],  # two versions
        ["mirascope.tags(['movie_project', 'version:0001'])"],  # different import
        ["ms.tags(['movie_project', 'version:0001'])"],  # different import
        ["tags()"],  # improper tags
    ],
)
@pytest.mark.parametrize(
    "command, expected_variables",
    [
        (
            MirascopeCommand.ADD,
            MirascopeCliVariables(prev_revision_id="0001", revision_id="0002"),
        ),
        (MirascopeCommand.USE, None),
    ],
)
@patch("mirascope.cli.utils.get_user_mirascope_settings")
@patch.object(Environment, "get_template")
@patch("mirascope.cli.utils.get_prompt_analyzer")
def test_write_prompt_to_template(
    mock_prompt_analyzer: MagicMock,
    mock_get_template: MagicMock,
    mock_settings: MagicMock,
    command: Literal[MirascopeCommand.ADD, MirascopeCommand.USE],
    expected_variables: MirascopeCliVariables,
    class_decorators: list[str],
    imports: list[tuple[str, Optional[str]]],
    from_imports: list[tuple[str, str, Optional[str]]],
    fixture_mirascope_user_settings,
):
    """Tests that a prompt is properly created from the template"""

    sample_file_content = ""

    mock_settings.return_value = fixture_mirascope_user_settings

    mock_template = MagicMock()
    mock_template.render.return_value = _get_prompt_template()
    mock_get_template.return_value = mock_template
    prompt_analyzer = PromptAnalyzer()
    prompt_analyzer.imports = imports
    prompt_analyzer.from_imports = from_imports
    prompt_analyzer.comments = "A prompt for recommending movies of a particular genre."
    prompt_analyzer.classes = [
        ClassInfo(
            name="MovieRecommendationPrompt",
            docstring="Please recommend a list of movies in the {genre} category.",
            body="",
            bases=["BasePrompt"],
            decorators=class_decorators,
        ),
    ]
    mock_prompt_analyzer.return_value = prompt_analyzer

    write_prompt_to_template(sample_file_content, command, expected_variables)

    mock_settings.assert_called_once()
    mock_get_template.assert_called_with("prompt_template.j2")

    assert mock_template.render.call_args is not None


def test_find_file_names(tmp_path: Path):
    """Tests that the file names are properly found"""
    foo_dir = tmp_path / "foo"
    foo_dir.mkdir()
    (foo_dir / "public_foo.py").write_text("foo")
    (foo_dir / "_private.py").write_text("foo private")

    file_names = find_file_names(str(foo_dir))
    assert file_names == ["public_foo.py"]


@patch("mirascope.cli.utils.get_user_mirascope_settings")
def test_prompts_directory_files(
    get_user_mirascope_settings: MagicMock,
    fixture_mirascope_user_settings: MirascopeSettings,
    tmp_path: Path,
):
    """Tests that the prompts directory is properly found"""
    os.chdir(tmp_path)
    get_user_mirascope_settings.return_value = fixture_mirascope_user_settings
    prompts_directory = tmp_path / fixture_mirascope_user_settings.prompts_location
    prompts_directory.mkdir()
    (prompts_directory / "public_foo.py").write_text("foo")
    (prompts_directory / "_private.py").write_text("foo private")

    file_names = prompts_directory_files()
    assert file_names == ["public_foo"]


def test_parse_prompt_file_name():
    """Tests that the prompt file name is properly parsed"""
    prompt_file_name_with_extension = "0001_simple_prompt.py"
    prompt_file_name = "0001_simple_prompt"
    assert parse_prompt_file_name(prompt_file_name_with_extension) == prompt_file_name
    assert parse_prompt_file_name(prompt_file_name) == prompt_file_name
