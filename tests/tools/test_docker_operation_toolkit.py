from collections import namedtuple
from unittest.mock import MagicMock, patch

import pytest
from docker.errors import APIError, ImageNotFound

from mirascope.tools import DockerOperationToolKit, DockerOperationToolKitConfig
from mirascope.tools.system._docker_operation import DockerContainer

# Create ExecResult namedtuple to match docker's implementation
ExecResult = namedtuple("ExecResult", "exit_code,output")


@pytest.fixture
def mock_docker_client():
    """Creates a mock Docker client."""
    with patch("docker.from_env") as mock_client:
        # Mock container and its methods
        mock_container = MagicMock()
        mock_container.put_archive.return_value = True
        mock_container.stop.return_value = None

        # Initial exec result with the correct namedtuple format
        mock_container.exec_run.return_value = ExecResult(0, b"Test output")

        # Configure client to return mock container
        mock_client.return_value.containers.run.return_value = mock_container
        yield mock_client


@pytest.fixture
def docker_operation_toolkit(mock_docker_client):
    """Creates a DockerOperationToolKit instance with mocked Docker client."""
    config = DockerOperationToolKitConfig(
        docker_image="python:3.13-slim",
        max_memory="256m",
        allow_network=False,
    )
    return DockerOperationToolKit(
        config=config, docker_container=DockerContainer(config=config)
    )


def test_execute_python_without_custom_config(mock_docker_client):
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

    # Configure mock response
    mock_container = mock_docker_client.return_value.containers.run.return_value
    mock_container.exec_run.return_value = ExecResult(
        0, b"Hello from Python!\nResult: 2\n"
    )

    result = tool(code=code).call()  # pyright: ignore [reportCallIssue]
    assert "Hello from Python!" in result
    assert "Result: 2" in result


def test_execute_python(
    docker_operation_toolkit: DockerOperationToolKit, mock_docker_client
):
    """Test executing Python code."""
    code = """
print('Hello from Python!')
x = 1 + 1
print(f'Result: {x}')
"""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)

    # Configure mock response
    mock_container = mock_docker_client.return_value.containers.run.return_value
    mock_container.exec_run.return_value = ExecResult(
        0, b"Hello from Python!\nResult: 2\n"
    )

    result = tool(code=code, requirements=None).call()  # pyright: ignore [reportCallIssue]
    assert "Hello from Python!" in result
    assert "Result: 2" in result


def test_execute_python_with_requirements(mock_docker_client):
    """Test executing Python code with requirements."""
    code = """
import mirascope
print(mirascope)
"""
    config = DockerOperationToolKitConfig(
        docker_image="python:3.13-slim",
        max_memory="256m",
        allow_network=True,
    )
    docker_operation_toolkit = DockerOperationToolKit(
        config=config, docker_container=DockerContainer(config=config)
    )
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)

    # Configure mock responses
    mock_container = mock_docker_client.return_value.containers.run.return_value
    mock_container.exec_run.side_effect = [
        ExecResult(0, b"Successfully installed mirascope"),
        ExecResult(0, b"<module 'mirascope' from '/path/to/mirascope'>"),
    ]

    result = tool(code=code, requirements=["mirascope"]).call()  # pyright: ignore [reportCallIssue]
    assert result.startswith("<module 'mirascope' from")


def test_execute_python_with_requirements_network_disabled(
    docker_operation_toolkit: DockerOperationToolKit,
):
    """Test executing Python code with requirements when network is disabled."""
    code = ""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    result = tool(code=code, requirements=["mirascope"]).call()  # pyright: ignore [reportCallIssue]
    assert (
        result
        == "Error: Network access is disabled. Cannot install requirements via pip."
    )


def test_execute_shell(
    docker_operation_toolkit: DockerOperationToolKit, mock_docker_client
):
    """Test executing shell commands."""
    _, tool = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecuteShell)

    # Configure mock response
    mock_container = mock_docker_client.return_value.containers.run.return_value
    mock_container.exec_run.return_value = ExecResult(0, b"Hello from shell!\n")

    result = tool(command="echo 'Hello from shell!'").call()  # pyright: ignore [reportCallIssue]
    assert "Hello from shell!" in result


def test_execute_python_with_syntax_error(
    docker_operation_toolkit: DockerOperationToolKit, mock_docker_client
):
    """Test executing Python code with syntax error."""
    code = """
print('Hello'
x = 1 + 
"""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)

    # Configure mock response
    mock_container = mock_docker_client.return_value.containers.run.return_value
    mock_container.exec_run.return_value = ExecResult(1, b"SyntaxError: invalid syntax")

    result = tool(code=code).call()  # pyright: ignore [reportCallIssue]
    assert "SyntaxError" in result


def test_execute_shell_with_error(
    docker_operation_toolkit: DockerOperationToolKit, mock_docker_client
):
    """Test executing invalid shell command."""
    _, tool = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecuteShell)

    # Configure mock response
    mock_container = mock_docker_client.return_value.containers.run.return_value
    mock_container.exec_run.return_value = ExecResult(127, b"command not found")

    result = tool(command="nonexistent_command").call()  # pyright: ignore [reportCallIssue]
    assert "not found" in result.lower()


def test_container_error_handling(
    docker_operation_toolkit: DockerOperationToolKit, mock_docker_client
):
    """Test error handling when container operations fail."""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)
    tool_instance = tool(code="print('test')")  # pyright: ignore [reportCallIssue]

    # Mock container to raise an exception
    mock_container = mock_docker_client.return_value.containers.run.return_value
    mock_container.exec_run.side_effect = APIError("Container stopped")

    result = tool_instance.call()
    assert "Error executing code:" in result


def test_execute_python_with_file_creation(
    docker_operation_toolkit: DockerOperationToolKit, mock_docker_client
):
    """Test executing Python code that creates files."""
    code = """
with open('test.txt', 'w') as f:
    f.write('Hello from Python!')
print('File created')
"""
    tool, _ = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecutePython)

    # Configure mock response
    mock_container = mock_docker_client.return_value.containers.run.return_value
    mock_container.exec_run.return_value = ExecResult(0, b"File created")

    result = tool(code=code).call()  # pyright: ignore [reportCallIssue]
    assert "File created" in result


def test_execute_shell_with_pipe(
    docker_operation_toolkit: DockerOperationToolKit, mock_docker_client
):
    """Test executing shell commands with pipe."""
    _, tool = docker_operation_toolkit.create_tools()
    assert issubclass(tool, DockerOperationToolKit.ExecuteShell)

    # Configure mock response
    mock_container = mock_docker_client.return_value.containers.run.return_value
    mock_container.exec_run.return_value = ExecResult(0, b"Hello")

    result = tool(command="echo 'Hello' | grep 'Hello'").call()  # pyright: ignore [reportCallIssue]
    assert "Hello" in result


def test_container_cleanup_on_error(mock_docker_client):
    """Test container cleanup when initialization fails."""
    # Configure mock to raise ImageNotFound
    mock_docker_client.return_value.containers.run.side_effect = ImageNotFound(
        "Image not found"
    )

    config = DockerOperationToolKitConfig(
        docker_image="nonexistent:latest",
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
