import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from mirascope.tools import FileSystemToolkit, FileSystemToolkitConfig


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


def test_read_file(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test reading a file."""
    # Create a test file
    test_file = temp_dir / "test.txt"
    test_content = "Hello, World!"
    test_file.write_text(test_content)

    read_file = filesystem_toolkit.ReadFile(base_directory=temp_dir, path="test.txt")
    # Test reading
    result = read_file.call()
    assert result == test_content


def test_read_file_invalid_extension(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test reading a file with invalid extension."""
    read_file = filesystem_toolkit.ReadFile(base_directory=temp_dir, path="test.invalid")
    result = read_file.call()
    assert result.startswith("Error: Invalid file extension")


def test_read_file_not_found(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test reading a non-existent file."""
    read_file = filesystem_toolkit.ReadFile(base_directory=temp_dir, path="nonexistent.txt")
    result = read_file.call()
    assert result.startswith("Error: File")


def test_write_file(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test writing to a file."""
    content = "Test content"
    result =  filesystem_toolkit.WriteFile(base_directory=temp_dir, path="new.txt",content=content).call()
    assert result.startswith("Successfully")
    assert (temp_dir / "new.txt").read_text() == content


def test_write_file_too_large(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test writing content exceeding max file size."""
    large_content = "x" * 2000  # Larger than max_file_size
    result = filesystem_toolkit.WriteFile(base_directory=temp_dir, path="large.txt", content=large_content).call()
    assert result.startswith("Error: Content exceeds maximum size")


def test_list_directory(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test listing directory contents."""
    # Create test files
    (temp_dir / "file1.txt").write_text("test1")
    (temp_dir / "file2.txt").write_text("test2")

    result = filesystem_toolkit.ListDirectory(base_directory=temp_dir).call()
    assert "file1.txt" in result
    assert "file2.txt" in result


def test_create_directory(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test creating a directory."""
    test_dir = temp_dir / "testdir"
    test_dir.mkdir()
    result = filesystem_toolkit.ListDirectory(base_directory=temp_dir, path="testdir").call()
    assert result.startswith("Contents of testdir :\n")


def test_delete_file(filesystem_toolkit: FileSystemToolkit, temp_dir: Path):
    """Test deleting a file."""
    # Create test file
    test_file = temp_dir / "delete.txt"
    test_file.write_text("delete me")

    result =  filesystem_toolkit.DeleteFile(base_directory=temp_dir, path="delete.txt").call()
    assert result.startswith("Successfully")
    assert not test_file.exists()
