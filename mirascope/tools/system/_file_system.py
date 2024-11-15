from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from pydantic import Field, field_validator

from mirascope.core.base import toolkit_tool
from mirascope.tools.base import (
    ConfigurableTool,
    ConfigurableToolKit,
    _ConfigurableToolConfig,
)


class FileSystemToolKitConfig(_ConfigurableToolConfig):
    """Configuration for file_system toolkit"""

    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file size in bytes",
    )
    allowed_extensions: list[str] = Field(
        default=["txt", "md", "csv", "json", "yml", "yaml", "html"],
        description="List of allowed file extensions",
    )


class FileOperation(ConfigurableTool[FileSystemToolKitConfig], ABC):
    """Base class for file system operations."""

    __configurable_tool_config__ = FileSystemToolKitConfig()

    if TYPE_CHECKING:
        # In create_tools method, the base_directory is set to ToolKit base_directory
        base_directory: Path = Field(
            default=Path.cwd(), description="Base directory for file operations"
        )

    def _validate_path(self, path: str) -> str | None:
        """Validates file path for security and correctness.

        Args:
            path: The path to validate

        Returns:
            Optional[str]: Error message if validation fails, None if successful
        """
        file_path = self.base_directory / path

        try:
            file_path.resolve().relative_to(self.base_directory.resolve())
        except ValueError:
            return "Error: Invalid path (attempted path traversal)"

        return None

    def _validate_extension(self, path: str) -> str | None:
        """Validates file extension against allowed extensions.

        Args:
            path: The path to validate

        Returns:
            str | None: Error message if validation fails, None if successful
        """
        extension = Path(path).suffix.lstrip(".")
        if extension not in self._get_config().allowed_extensions:
            return f"Error: Invalid file extension. Allowed: {self._get_config().allowed_extensions}"
        return None


class FileSystemToolKit(ConfigurableToolKit[FileSystemToolKitConfig]):
    """ToolKit for file system operations.
    Read, write, list, create, and delete files and directories.
    """

    config: FileSystemToolKitConfig = FileSystemToolKitConfig()

    @toolkit_tool
    class ReadFile(FileOperation):
        """Tool for reading file contents."""

        path: str

        def call(self) -> str:
            """Read and return file contents.

            Returns:
                str: File contents or error message if operation fails
            """
            if error := self._validate_path(self.path):
                return error

            if error := self._validate_extension(self.path):
                return error

            file_path = self.base_directory / self.path
            if not file_path.is_file():
                return f"Error: File {self.path} not found"

            try:
                if file_path.stat().st_size > self._get_config().max_file_size:
                    return f"Error: File exceeds maximum size of {self._get_config().max_file_size} bytes"

                return file_path.read_text()
            except Exception as e:  # pragma: no cover
                return f"Error reading file: {str(e)}"

    @toolkit_tool
    class WriteFile(FileOperation):
        """Tool for writing content to a file."""

        path: str
        content: str

        def call(self) -> str:
            """Write content to file and return status.

            Returns:
                str: Success message or error message if operation fails
            """
            if error := self._validate_path(self.path):
                return error

            if error := self._validate_extension(self.path):
                return error

            file_path = self.base_directory / self.path
            try:
                content_size = len(self.content.encode("utf-8"))
                if content_size > self._get_config().max_file_size:
                    return f"Error: Content exceeds maximum size of {self._get_config().max_file_size} bytes"

                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(self.content)
                return f"Successfully wrote to {self.path}"
            except Exception as e:  # pragma: no cover
                return f"Error writing file: {str(e)}"

    @toolkit_tool
    class ListDirectory(FileOperation):
        """Tool for listing directory contents."""

        path: str = Field(default="")

        def call(self) -> str:
            """List directory contents and return formatted string.

            Returns:
                str: Formatted directory listing or error message if operation fails
            """

            if error := self._validate_path(self.path):
                return error

            dir_path = self.base_directory / self.path
            if not dir_path.is_dir():
                return f"Error: Directory {self.path} not found"

            try:
                contents: list[dict[str, str | int | None]] = []
                for item in dir_path.iterdir():
                    item_type = "file" if item.is_file() else "directory"
                    size = item.stat().st_size if item.is_file() else None
                    contents.append(
                        {"name": item.name, "type": item_type, "size": size}
                    )

                output = f"Contents of {self.path or '.'} :\n"
                for item in contents:
                    size_info = (
                        f" ({item['size']} bytes)" if item["size"] is not None else ""
                    )
                    output += f"- {item['name']} [{item['type']}]{size_info}\n"

                return output
            except Exception as e:  # pragma: no cover
                return f"Error listing directory: {str(e)}"

    @toolkit_tool
    class CreateDirectory(FileOperation):
        """Tool for creating directories."""

        path: str

        def call(self) -> str:
            """Create directory and return status.

            Returns:
                str: Success message or error message if operation fails
            """
            if error := self._validate_path(self.path):
                return error

            dir_path = self.base_directory / self.path
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                return f"Successfully created directory {self.path}"
            except Exception as e:
                return f"Error creating directory: {str(e)}"

    @toolkit_tool
    class DeleteFile(FileOperation):
        """Tool for deleting files."""

        path: str

        def call(self) -> str:
            """Delete file and return status.

            Returns:
                str: Success message or error message if operation fails
            """
            if error := self._validate_path(self.path):
                return error

            if error := self._validate_extension(self.path):
                return error

            file_path = self.base_directory / self.path
            try:
                if not file_path.exists():
                    return f"Error: File {self.path} not found"

                if not file_path.is_file():
                    return f"Error: {self.path} is not a file"

                file_path.unlink()
                return f"Successfully deleted {self.path}"
            except Exception as e:  # pragma: no cover
                return f"Error deleting file: {str(e)}"

    __configurable_tool_config__ = FileSystemToolKitConfig()
    __namespace__ = "file_system"
    __prompt_usage_description__: ClassVar[str] = """
    - Tools for file system operations:
        - ReadFile: Reads content from a file
        - WriteFile: Writes content to a file
        - ListDirectory: Lists directory contents
        - CreateDirectory: Creates a new directory
        - DeleteFile: Deletes a file
    """

    base_directory: Path = Field(
        default=Path.cwd(), description="Base directory for file operations"
    )

    @field_validator("base_directory")
    def validate_base_directory(cls, v: Path) -> Path:
        """Validates that the base directory exists and is a directory.

        Args:
            v: The path to validate

        Returns:
            Path: The validated path

        Raises:
            ValueError: If the path doesn't exist or isn't a directory
        """
        if not v.exists():
            raise ValueError(f"Base directory {v} does not exist")
        if not v.is_dir():
            raise ValueError(f"{v} is not a directory")
        return v
