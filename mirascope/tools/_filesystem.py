from pathlib import Path
from typing import ClassVar

from pydantic import Field, field_validator

from mirascope.core.base import toolkit_tool
from mirascope.tools.base import ConfigurableToolKit, _ToolConfig


class FileSystemToolkitConfig(_ToolConfig):
    """Configuration for filesystem toolkit"""

    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file size in bytes",
    )
    allowed_extensions: list[str] = Field(
        default=["txt", "md", "csv", "json", "yml", "yaml"],
        description="List of allowed file extensions",
    )


class FileSystemToolkit(ConfigurableToolKit[FileSystemToolkitConfig]):
    """Toolkit for filesystem operations."""

    __config__ = FileSystemToolkitConfig()
    __namespace__ = "filesystem"
    __prompt_usage_description__: ClassVar[str] = """
    - Tools for filesystem operations:
        - read_file: Reads content from a file
        - write_file: Writes content to a file
        - list_directory: Lists directory contents
        - create_directory: Creates a new directory
        - delete_file: Deletes a file
    """

    base_directory: Path = Field(
        default=Path.cwd(), description="Base directory for file operations"
    )

    @field_validator("base_directory")
    def validate_base_directory(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Base directory {v} does not exist")
        if not v.is_dir():
            raise ValueError(f"{v} is not a directory")
        return v

    def _validate_path(self, path: str) -> str | None:
        """Validates file path and returns error message if invalid."""
        file_path = self.base_directory / path

        # Check for path traversal attempts
        try:
            file_path.resolve().relative_to(self.base_directory.resolve())
        except ValueError:
            return "Error: Invalid path (attempted path traversal)"

        return None

    def _validate_extension(self, path: str) -> str | None:
        """Validates file extension and returns error message if invalid."""
        extension = Path(path).suffix.lstrip(".")
        if extension not in self._config().allowed_extensions:
            return f"Error: Invalid file extension. Allowed: {self._config().allowed_extensions}"
        return None

    @toolkit_tool
    def read_file(self, path: str) -> str:
        """Reads content from a file.

        base_directory: {self.base_directory}

        Args:
            path: Path to the file
        Returns:
            File content
        """
        if error := self._validate_path(path):
            return error

        if error := self._validate_extension(path):
            return error

        file_path = self.base_directory / path
        if not file_path.is_file():
            return f"Error: File {path} not found"

        try:
            if file_path.stat().st_size > self._config().max_file_size:
                return f"Error: File exceeds maximum size of {self._config().max_file_size} bytes"

            return file_path.read_text()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @toolkit_tool
    def write_file(self, path: str, content: str) -> str:
        """Writes content to a file.

        base_directory: {self.base_directory}

        Args:
            path: Path to the file
        Returns:
            Success message or error message
        """
        if error := self._validate_path(path):
            return error

        if error := self._validate_extension(path):
            return error

        file_path = self.base_directory / path
        try:
            # Check content size
            content_size = len(content.encode("utf-8"))
            if content_size > self._config().max_file_size:
                return f"Error: Content exceeds maximum size of {self._config().max_file_size} bytes"

            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            file_path.write_text(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    @toolkit_tool
    def list_directory(self, path: str = "") -> str:
        """Lists directory contents.

         base_directory: {self.base_directory}

        Args:
            path: Path to the file (default: {self.base_directory})
        Returns:
            Directory contents
        """
        if error := self._validate_path(path):
            return error

        dir_path = self.base_directory / path
        if not dir_path.is_dir():
            return f"Error: Directory {path} not found"

        try:
            contents = []
            for item in dir_path.iterdir():
                item_type = "file" if item.is_file() else "directory"
                size = item.stat().st_size if item.is_file() else None
                contents.append({"name": item.name, "type": item_type, "size": size})

            # Format output
            output = f"Contents of {path or '.'} :\n"
            for item in contents:
                size_info = (
                    f" ({item['size']} bytes)" if item["size"] is not None else ""
                )
                output += f"- {item['name']} [{item['type']}]{size_info}\n"

            return output
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    @toolkit_tool
    def create_directory(self, path: str) -> str:
        """Creates a new directory.

        base_directory: {self.base_directory}

        Args:
            path: Path to the new directory
        Returns:
            Success message or error message
        """
        if error := self._validate_path(path):
            return error

        dir_path = self.base_directory / path
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory {path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"

    @toolkit_tool
    def delete_file(self, path: str) -> str:
        """Deletes a file.

        base_directory: {self.base_directory}

        Args:
            path: Path to the file
        Returns:
            Success message or error message
        """
        if error := self._validate_path(path):
            return error

        if error := self._validate_extension(path):
            return error

        file_path = self.base_directory / path
        try:
            if not file_path.exists():
                return f"Error: File {path} not found"

            if not file_path.is_file():
                return f"Error: {path} is not a file"

            file_path.unlink()
            return f"Successfully deleted {path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
