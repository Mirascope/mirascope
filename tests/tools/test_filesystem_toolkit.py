import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import TypeVar

import pytest

from mirascope.tools import FileSystemToolKit, FileSystemToolKitConfig
from mirascope.tools.system._file_system import FileOperation


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Creates a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def filesystem_toolkit(temp_dir: Path) -> FileSystemToolKit:
    """Creates a FileSystemToolKit instance with a temporary directory."""
    config = FileSystemToolKitConfig(
        max_file_size=1024,  # 1KB for testing
        allowed_extensions=["txt", "md"],
    )
    return FileSystemToolKit(
        config=config,
        base_directory=temp_dir,
    )


_FileOperationT = TypeVar("_FileOperationT", bound=FileOperation)


def _get_tool_type(
    toolkit: FileSystemToolKit, target_tool_type: type[_FileOperationT]
) -> type[_FileOperationT]:
    return [t for t in toolkit.create_tools() if issubclass(t, target_tool_type)][0]


def test_read_file(filesystem_toolkit: FileSystemToolKit, temp_dir: Path):
    """Test reading a file."""
    # Create a test file
    test_file = temp_dir / "test.txt"
    test_content = "Hello, World!"
    test_file.write_text(test_content)
    read_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.ReadFile)
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
        FileSystemToolKit(base_directory=temp_dir), FileSystemToolKit.ReadFile
    )
    # Test reading
    assert issubclass(read_file, FileSystemToolKit.ReadFile)
    result = read_file(path="test.txt").call()
    assert result == test_content


def test_read_file_invalid_extension(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test reading a file with invalid extension."""

    read_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.ReadFile)
    result = read_file(path="test.invalid").call()
    assert result.startswith("Error: Invalid file extension")


def test_read_file_not_found(filesystem_toolkit: FileSystemToolKit, temp_dir: Path):
    """Test reading a non-existent file."""
    read_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.ReadFile)
    result = read_file(path="nonexistent.txt").call()
    assert result.startswith("Error: File")


def test_write_file(filesystem_toolkit: FileSystemToolKit, temp_dir: Path):
    """Test writing to a file."""
    content = "Test content"
    write_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.WriteFile)
    result = write_file(path="new.txt", content=content).call()
    assert result.startswith("Successfully")
    assert (temp_dir / "new.txt").read_text() == content


def test_write_file_too_large(filesystem_toolkit: FileSystemToolKit, temp_dir: Path):
    """Test writing content exceeding max file size."""
    large_content = "x" * 2000  # Larger than max_file_size
    write_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.WriteFile)
    result = write_file(path="large.txt", content=large_content).call()
    assert result.startswith("Error: Content exceeds maximum size")


def test_list_directory(filesystem_toolkit: FileSystemToolKit, temp_dir: Path):
    """Test listing directory contents."""
    # Create test files
    (temp_dir / "file1.txt").write_text("test1")
    (temp_dir / "file2.txt").write_text("test2")

    list_directory = _get_tool_type(filesystem_toolkit, FileSystemToolKit.ListDirectory)
    result = list_directory(path=str(temp_dir)).call()
    assert "file1.txt" in result
    assert "file2.txt" in result


def test_create_directory(filesystem_toolkit: FileSystemToolKit, temp_dir: Path):
    """Test creating a directory."""
    test_dir = temp_dir / "testdir"
    test_dir.mkdir()
    list_directory = _get_tool_type(filesystem_toolkit, FileSystemToolKit.ListDirectory)
    result = list_directory(path="testdir").call()
    assert result.startswith("Contents of testdir :\n")


def test_delete_file(filesystem_toolkit: FileSystemToolKit, temp_dir: Path):
    """Test deleting a file."""
    # Create test file
    test_file = temp_dir / "delete.txt"
    test_file.write_text("delete me")

    delete_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.DeleteFile)
    result = delete_file(path="delete.txt").call()
    assert result.startswith("Successfully")
    assert not test_file.exists()


def test_read_file_too_large(filesystem_toolkit: FileSystemToolKit, temp_dir: Path):
    """Test reading a file that exceeds max file size."""
    test_file = temp_dir / "large.txt"
    test_file.write_text("x" * 2000)  # Larger than max_file_size
    read_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.ReadFile)
    result = read_file(path="large.txt").call()
    assert result.startswith("Error: File exceeds maximum size")


def test_read_file_path_traversal(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test reading a file with path traversal attempt."""
    read_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.ReadFile)
    result = read_file(path="../../../etc/passwd").call()
    assert result.startswith("Error: Invalid path")


def test_write_file_path_traversal(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test writing a file with path traversal attempt."""
    write_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.WriteFile)
    result = write_file(path="../../../tmp/test.txt", content="test").call()
    assert result.startswith("Error: Invalid path")


def test_list_directory_path_traversal(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test listing directory with path traversal attempt."""
    list_directory = _get_tool_type(filesystem_toolkit, FileSystemToolKit.ListDirectory)
    result = list_directory(path="../../../etc").call()
    assert result.startswith("Error: Invalid path")


def test_list_directory_not_found(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test listing non-existent directory."""
    list_directory = _get_tool_type(filesystem_toolkit, FileSystemToolKit.ListDirectory)
    result = list_directory(path="nonexistent").call()
    assert result.startswith("Error: Directory")


def test_create_directory_path_traversal(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test creating directory with path traversal attempt."""
    create_directory = _get_tool_type(
        filesystem_toolkit, FileSystemToolKit.CreateDirectory
    )
    result = create_directory(path="../../../tmp/newdir").call()
    assert result.startswith("Error: Invalid path")


def test_create_existing_directory(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test creating an already existing directory."""
    create_directory = _get_tool_type(
        filesystem_toolkit, FileSystemToolKit.CreateDirectory
    )

    # First creation
    result1 = create_directory(path="existingdir").call()
    assert result1.startswith("Successfully")

    # Second creation of same directory
    result2 = create_directory(path="existingdir").call()
    assert result2.startswith("Successfully")  # Should succeed due to exist_ok=True


def test_create_directory_permission_error(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test creating directory with insufficient permissions."""
    # Create a directory with restricted permissions
    restricted_dir = temp_dir / "restricted"
    restricted_dir.mkdir()
    restricted_dir.chmod(0o000)  # Remove all permissions

    create_directory = _get_tool_type(
        filesystem_toolkit, FileSystemToolKit.CreateDirectory
    )
    result = create_directory(path="restricted/newdir").call()
    assert result.startswith("Error creating directory")

    # Cleanup
    restricted_dir.chmod(0o755)  # Restore permissions for cleanup


def test_delete_file_not_found(filesystem_toolkit: FileSystemToolKit, temp_dir: Path):
    """Test deleting a non-existent file."""
    delete_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.DeleteFile)
    result = delete_file(path="nonexistent.txt").call()
    assert result.startswith("Error: File")


def test_delete_file_path_traversal(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test deleting file with path traversal attempt."""
    delete_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.DeleteFile)
    result = delete_file(path="../../../etc/passwd").call()
    assert result.startswith("Error: Invalid path")


def test_delete_directory_as_file(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test attempting to delete a directory using delete_file."""
    # Create a directory
    test_dir = temp_dir / "testdir.txt"
    test_dir.mkdir()

    delete_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.DeleteFile)
    result = delete_file(path="testdir.txt").call()
    assert result.startswith("Error: testdir.txt is not a file")


def test_invalid_base_directory():
    """Test toolkit creation with invalid base directory."""
    with pytest.raises(ValueError):
        FileSystemToolKit(base_directory=Path("/nonexistent/directory"))


def test_base_directory_is_file(temp_dir: Path):
    """Test toolkit creation when base_directory is a file."""
    test_file = temp_dir / "file.txt"
    test_file.write_text("test")

    with pytest.raises(ValueError):
        FileSystemToolKit(base_directory=test_file)


def test_write_file_invalid_extension(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test writing a file with invalid extension."""
    write_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.WriteFile)
    result = write_file(path="test.invalid", content="test").call()
    assert result.startswith("Error: Invalid file extension")


def test_delete_file_invalid_extension(
    filesystem_toolkit: FileSystemToolKit, temp_dir: Path
):
    """Test deleting a file with invalid extension."""
    test_file = temp_dir / "test.invalid"
    test_file.write_text("test")
    delete_file = _get_tool_type(filesystem_toolkit, FileSystemToolKit.DeleteFile)
    result = delete_file(path="test.invalid").call()
    assert result.startswith("Error: Invalid file extension")


def test_usage_description(filesystem_toolkit: FileSystemToolKit):
    """filesystem_toolkit description."""
    assert (
        filesystem_toolkit.usage_description()
        == """- Tools for file system operations:
    - ReadFile: Reads content from a file
    - WriteFile: Writes content to a file
    - ListDirectory: Lists directory contents
    - CreateDirectory: Creates a new directory
    - DeleteFile: Deletes a file"""
    )
