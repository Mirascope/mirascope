import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import TypeVar

import pytest

from mirascope.tools import FileSystemToolkit, FileSystemToolkitConfig
from mirascope.tools.system._filesystem import FileOperation


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Creates a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def filesystem_toolkit(temp_dir: Path) -> FileSystemToolkit:
    """Creates a FileSystemToolkit instance with a temporary directory."""
    config = FileSystemToolkitConfig(
        max_file_size=1024,  # 1KB for testing
        allowed_extensions=["txt", "md"],
    )
    return FileSystemToolkit.from_config(config)(
        base_directory=temp_dir,
    )


_FileOperationT = TypeVar("_FileOperationT", bound=FileOperation)


def _get_tool_type(
    toolkit: FileSystemToolkit, target_tool_type: type[_FileOperationT]
) -> type[_FileOperationT]:
    return [t for t in toolkit.create_tools() if issubclass(t, target_tool_type)][0]


def test_read_file(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test reading a file."""
    # Create a test file
    test_file = temp_dir / "test.txt"
    test_content = "Hello, World!"
    test_file.write_text(test_content)
    read_file = _get_tool_type(filesystem_toolkit, FileSystemToolkit.ReadFile)
    # Test reading
    result = read_file(path="test.txt").call()
    assert result == test_content


def test_read_file_with_default_config(temp_dir: Path):
    """Test reading a file."""
    # Create a test file
    test_file = temp_dir / "test.txt"
    test_content = "Hello, World!"
    test_file.write_text(test_content)
    read_file = _get_tool_type(
        FileSystemToolkit(base_directory=temp_dir), FileSystemToolkit.ReadFile
    )
    # Test reading
    assert issubclass(read_file, FileSystemToolkit.ReadFile)
    result = read_file(path="test.txt").call()
    assert result == test_content


def test_read_file_invalid_extension(
    filesystem_toolkit: FileSystemToolkit, temp_dir: Path
):
    """Test reading a file with invalid extension."""

    read_file = _get_tool_type(filesystem_toolkit, FileSystemToolkit.ReadFile)
    result = read_file(path="test.invalid").call()
    assert result.startswith("Error: Invalid file extension")


def test_read_file_not_found(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test reading a non-existent file."""
    read_file = _get_tool_type(filesystem_toolkit, FileSystemToolkit.ReadFile)
    result = read_file(path="nonexistent.txt").call()
    assert result.startswith("Error: File")


def test_write_file(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test writing to a file."""
    content = "Test content"
    write_file = _get_tool_type(filesystem_toolkit, FileSystemToolkit.WriteFile)
    result = write_file(path="new.txt", content=content).call()
    assert result.startswith("Successfully")
    assert (temp_dir / "new.txt").read_text() == content


def test_write_file_too_large(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test writing content exceeding max file size."""
    large_content = "x" * 2000  # Larger than max_file_size
    write_file = _get_tool_type(filesystem_toolkit, FileSystemToolkit.WriteFile)
    result = write_file(path="large.txt", content=large_content).call()
    assert result.startswith("Error: Content exceeds maximum size")


def test_list_directory(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test listing directory contents."""
    # Create test files
    (temp_dir / "file1.txt").write_text("test1")
    (temp_dir / "file2.txt").write_text("test2")

    list_directory = _get_tool_type(filesystem_toolkit, FileSystemToolkit.ListDirectory)
    result = list_directory(path=str(temp_dir)).call()
    assert "file1.txt" in result
    assert "file2.txt" in result


def test_create_directory(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test creating a directory."""
    test_dir = temp_dir / "testdir"
    test_dir.mkdir()
    list_directory = _get_tool_type(filesystem_toolkit, FileSystemToolkit.ListDirectory)
    result = list_directory(path="testdir").call()
    assert result.startswith("Contents of testdir :\n")


def test_delete_file(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test deleting a file."""
    # Create test file
    test_file = temp_dir / "delete.txt"
    test_file.write_text("delete me")

    delete_file = _get_tool_type(filesystem_toolkit, FileSystemToolkit.DeleteFile)
    result = delete_file(path="delete.txt").call()
    assert result.startswith("Successfully")
    assert not test_file.exists()
