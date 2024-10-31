from __future__ import annotations

import io
import tarfile
from collections.abc import Generator
from contextlib import contextmanager
from typing import ClassVar

import docker
from docker.models.containers import Container
from pydantic import Field

from mirascope.core import toolkit_tool
from mirascope.tools.base import ConfigurableToolKit, _ToolConfig


class ComputerUseToolkitConfig(_ToolConfig):
    """Configuration for computer use toolkit"""

    docker_image: str = Field(
        default="python:3.13-slim", description="Docker image for code execution"
    )
    max_memory: str = Field(default="512m", description="Maximum memory allocation")
    allow_network: bool = Field(default=True, description="Allow network access")


class ComputerUseToolkit(ConfigurableToolKit[ComputerUseToolkitConfig]):
    """Toolkit for executing Python code and shell commands in a Docker container."""

    __config__ = ComputerUseToolkitConfig()
    __namespace__ = "computer"
    __prompt_usage_description__: ClassVar[str] = """
    - Tools for code execution:
        - execute_python: Executes Python code in a Docker container
        - execute_shell: Executes shell commands in a Docker container
        - install_package: Installs a Python package in the container
    """

    def _setup_container(self) -> Container:
        """Sets up a persistent container for code execution."""
        client = docker.from_env()
        return client.containers.run(
            self._config().docker_image,
            "tail -f /dev/null",  # Keep container running
            detach=True,
            mem_limit=self._config().max_memory,
            network_disabled=not self._config().allow_network,
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

    @toolkit_tool
    def execute_python(self, code: str, requirements: list[str] | None) -> str:
        """Executes Python code in a Docker container.

        docker_image: {self.__config__.docker_image}
        allow_network: {self.__config__.allow_network}

        Args:
            self: ComputerUseToolkit instance
            code: Python code to execute
            requirements: List of Python package requirements to install
        """

        try:
            contents = {
                "main.py": code,
            }
            if requirements:
                if not self._config().allow_network:
                    return "Error: Network access is disabled. Cannot install requirements via pip."
                contents["requirements.txt"] = "\n".join(requirements)
            stream = self._create_tar_stream(contents)
            with self._container_context() as container:
                container.put_archive("/", stream)
                if requirements:
                    exit_code, output = container.exec_run(
                        cmd=["pip", "install", "-r", "/requirements.txt"],
                    )
                    if exit_code != 0:
                        return (
                            f"Error installing requirements: {output.decode('utf-8')}"
                        )
                exit_code, output = container.exec_run(
                    cmd=["python", "/main.py"],
                )
            return output.decode("utf-8")

        except Exception as e:
            return f"Error executing code: {str(e)}"

    @toolkit_tool
    def execute_shell(self, command: str) -> str:
        """Executes shell commands in a Docker container.

        docker_image: {self.__config__.docker_image}
        allow_network: {self.__config__.allow_network}

        Args:
            command: Shell command to execute
        """
        try:
            with self._container_context() as container:
                exec_result = container.exec_run(
                    cmd=["sh", "-c", command],
                )
            return exec_result.output.decode("utf-8")
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @contextmanager
    def _container_context(self) -> Generator[Container, None, None]:
        """Context manager for Docker container."""
        container = self._setup_container()
        try:
            yield container
        finally:
            container.stop()
