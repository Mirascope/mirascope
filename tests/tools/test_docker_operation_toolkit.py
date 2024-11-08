from typing import cast

import pytest

from mirascope.tools import DockerOperationToolKit, DockerOperationToolKitConfig
from mirascope.tools.system._docker_operation import DockerContainer, DockerOperation


@pytest.fixture
def docker_operation_toolkit() -> DockerOperationToolKit:
    """Creates a DockerOperationToolKit instance."""
    config = DockerOperationToolKitConfig(
        docker_image="python:3.13-slim",
        max_memory="256m",
        allow_network=False,  # Safer for testing
    )
    return DockerOperationToolKit(
        config=config, docker_container=DockerContainer(config=config)
    )


def test_execute_python_without_custom_config():
    """Test executing Python code without custom configuration."""
    docker_operation_toolkit = DockerOperationToolKit(
        docker_container=DockerContainer()
    )
    code = """
print('Hello from Python!')
x = 1 + 1
print(f'Result: {x}')
"""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    result = tool(code=code).call()  # pyright: ignore [reportCallIssue]
    assert "Hello from Python!" in result
    assert "Result: 2" in result


def test_execute_python(docker_operation_toolkit: DockerOperationToolKit):
    """Test executing Python code."""
    code = """
print('Hello from Python!')
x = 1 + 1
print(f'Result: {x}')
"""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    result = tool(code=code, requirements=None).call()  # pyright: ignore [reportCallIssue]
    assert "Hello from Python!" in result
    assert "Result: 2" in result


def test_execute_python_with_requirements(
    docker_operation_toolkit: DockerOperationToolKit,
):
    """Test executing Python code with requirements."""
    code = """
import mirascope
print(mirascope)
"""
    config = DockerOperationToolKitConfig(
        docker_image="python:3.13-slim",
        max_memory="256m",
        allow_network=True,  # To use pip install
    )
    tool, _ = DockerOperationToolKit(
        config=config, docker_container=DockerContainer(config=config)
    ).create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    result = tool(code=code, requirements=["mirascope"]).call()  # pyright: ignore [reportCallIssue]
    assert result.startswith("<module 'mirascope' from")


def test_execute_python_with_requirements_network_disabled(
    docker_operation_toolkit: DockerOperationToolKit,
):
    """Test executing Python code with requirements."""
    code = ""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    result = tool(code=code, requirements=["mirascope"]).call()  # pyright: ignore [reportCallIssue]
    assert (
        result
        == "Error: Network access is disabled. Cannot install requirements via pip."
    )


def test_execute_shell(docker_operation_toolkit: DockerOperationToolKit):
    """Test executing shell commands."""
    _, tool = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecuteShell)
    result = tool(command="echo 'Hello from shell!'").call()  # pyright: ignore [reportCallIssue]
    assert "Hello from shell!" in result


def test_execute_python_with_syntax_error(
    docker_operation_toolkit: DockerOperationToolKit,
):
    """Test executing Python code with syntax error."""
    code = """
print('Hello'
x = 1 + 
"""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    result = tool(code=code).call()  # pyright: ignore [reportCallIssue]
    assert "SyntaxError" in result


def test_execute_shell_with_error(docker_operation_toolkit: DockerOperationToolKit):
    """Test executing invalid shell command."""
    _, tool = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecuteShell)
    result = tool(command="nonexistent_command").call()  # pyright: ignore [reportCallIssue]
    assert "not found" in result.lower()


def test_container_error_handling(docker_operation_toolkit: DockerOperationToolKit):
    """Test error handling when container operations fail."""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    tool_instance = tool(code="print('test')")  # pyright: ignore [reportCallIssue]

    # Force container to stop to simulate error
    container = cast(DockerOperation, tool_instance)._docker_container.container
    container.stop()

    # Next execution should handle the error and create a new container
    result = tool_instance.call()
    assert "Error executing code:" in result


def test_execute_python_with_file_creation(
    docker_operation_toolkit: DockerOperationToolKit,
):
    """Test executing Python code that creates files."""
    code = """
with open('test.txt', 'w') as f:
    f.write('Hello from Python!')
print('File created')
"""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    result = tool(code=code).call()  # pyright: ignore [reportCallIssue]
    assert "File created" in result


def test_execute_shell_with_pipe(docker_operation_toolkit: DockerOperationToolKit):
    """Test executing shell commands with pipe."""
    _, tool = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecuteShell)
    result = tool(command="echo 'Hello' | grep 'Hello'").call()  # pyright: ignore [reportCallIssue]
    assert "Hello" in result


def test_container_cleanup_on_error():
    """Test container cleanup when initialization fails."""
    config = DockerOperationToolKitConfig(
        docker_image="nonexistent:latest",  # Invalid image
        max_memory="256m",
        allow_network=False,
    )
    toolkit = DockerOperationToolKit(
        config=config, docker_container=DockerContainer(config=config)
    )
    tool, _ = toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    result = tool(code="print('test')").call()  # pyright: ignore [reportCallIssue]
    assert "Error" in result


def test_usage_description(docker_operation_toolkit: DockerOperationToolKit):
    """Test usage description."""
    assert (
        docker_operation_toolkit.usage_description()
        == """- Tools for code execution:
    - ExecutePython: Executes Python code with optional requirements in a Docker container
    - ExecuteShell: Executes shell commands in a Docker container"""
    )
