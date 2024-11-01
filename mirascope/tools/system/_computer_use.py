from __future__ import annotations

import io
import tarfile
from abc import ABC
from contextlib import suppress
from typing import ClassVar

import docker
from docker.models.containers import Container
from pydantic import Field

from mirascope.core import toolkit_tool
from mirascope.tools.base import (
    ConfigurableTool,
    ConfigurableToolKit,
    _ToolConfig,
    _ToolSchemaT,
)


class ComputerUseToolkitConfig(_ToolConfig):
    """Configuration for computer use toolkit"""

    docker_image: str = Field(
        default="python:3.13-slim", description="Docker image for code execution"
    )
    max_memory: str = Field(default="512m", description="Maximum memory allocation")
    allow_network: bool = Field(default=True, description="Allow network access")


class DockerOperation(ConfigurableTool[ComputerUseToolkitConfig, _ToolSchemaT], ABC):
    """Base class for Docker operations."""

    __config__ = ComputerUseToolkitConfig()
    __container__: Container | None = None

    @property
    def _container(self) -> Container:
        """Returns the Docker container for code execution."""
        if self.__container__ is None:
            self.__container__ = self._setup_container()
        return self.__container__

    def __del__(self) -> None:
        """Cleanup the container when the toolkit is destroyed."""
        if container := self.__container__:
            with suppress(Exception):
                container.stop()

    def _setup_container(self) -> Container:
        """Sets up a persistent container for code execution."""
        client = docker.from_env()
        return client.containers.run(
            self._get_config().docker_image,
            "tail -f /dev/null",  # Keep container running
            detach=True,
            mem_limit=self._get_config().max_memory,
            network_disabled=not self._get_config().allow_network,
            remove=True,
            security_opt=["no-new-privileges"],  # Prevent privilege escalation
            cap_drop=["ALL"],  # Drop all capabilities
        )

    @classmethod
    def _create_tar_stream(cls, files: dict[str, str]) -> io.BytesIO:
        """Creates a tar stream from a dictionary of files."""
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w") as tar:
            for name, content in files.items():
                info = tarfile.TarInfo(name=name)
                encoded_content = content.encode("utf-8")
                info.size = len(encoded_content)
                tar.addfile(info, io.BytesIO(encoded_content))
        stream.seek(0)
        return stream


class ComputerUseToolkit(ConfigurableToolKit[ComputerUseToolkitConfig]):
    """Toolkit for executing Python code and shell commands in a Docker container."""

    __config__ = ComputerUseToolkitConfig()
    __namespace__ = "computer"
    __prompt_usage_description__: ClassVar[str] = """
    - Tools for code execution:
        - ExecutePython: Executes Python code with optional requirements in a Docker container
        - execute_shell: Executes shell commands in a Docker container
    """

    @toolkit_tool
    class ExecutePython(DockerOperation):
        """Tool for executing Python code in a Docker container."""

        code: str
        requirements: list[str] | None = None

        def call(self) -> str:
            """Executes Python code in a Docker container.

            docker_image: {self.__config__.docker_image}
            allow_network: {self.__config__.allow_network}

            Returns:
                str: Output of the code execution
            """
            try:
                contents = {
                    "main.py": self.code,
                }
                if self.requirements:
                    if not self._get_config().allow_network:
                        return "Error: Network access is disabled. Cannot install requirements via pip."
                    contents["requirements.txt"] = "\n".join(self.requirements)
                stream = self._create_tar_stream(contents)
                self._container.put_archive("/", stream)
                if self.requirements:
                    exit_code, output = self._container.exec_run(
                        cmd=["pip", "install", "-r", "/requirements.txt"],
                    )
                    if exit_code != 0:  # pragma: no cover
                        return (
                            f"Error installing requirements: {output.decode('utf-8')}"
                        )
                exit_code, output = self._container.exec_run(
                    cmd=["python", "/main.py"],
                )
                return output.decode("utf-8")

            except Exception as e:
                return f"Error executing code: {str(e)}"

    @toolkit_tool
    class ExecuteShell(DockerOperation):
        """Tool for executing shell commands in a Docker container."""

        command: str

        def call(self) -> str:
            """Executes shell commands in a Docker container.

            docker_image: {self.__config__.docker_image}
            allow_network: {self.__config__.allow_network}

            Returns:
                str: Output of the command execution
            """
            try:
                exec_result = self._container.exec_run(
                    cmd=["sh", "-c", self.command],
                )
                return exec_result.output.decode("utf-8")
            except Exception as e:  # pragma: no cover
                return f"Error executing command: {str(e)}"
