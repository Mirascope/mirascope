from typing import cast

import docker
import pytest

from mirascope.tools import ComputerUseToolkit, ComputerUseToolkitConfig
from mirascope.tools.system._computer_use import DockerOperation


@pytest.fixture
def computer_toolkit() -> ComputerUseToolkit:
    """Creates a ComputerUseToolkit instance."""
    config = ComputerUseToolkitConfig(
        docker_image="python:3.13-slim",
        max_memory="256m",
        allow_network=False,  # Safer for testing
    )
    return ComputerUseToolkit.from_config(config)()


def test_execute_python_without_custom_config():
    """Test executing Python code without custom configuration."""
    computer_toolkit = ComputerUseToolkit()
    code = """
print('Hello from Python!')
x = 1 + 1
print(f'Result: {x}')
"""
    tool, _ = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    result = tool(code=code).call()
    assert "Hello from Python!" in result
    assert "Result: 2" in result


def test_execute_python(computer_toolkit: ComputerUseToolkit):
    """Test executing Python code."""
    code = """
print('Hello from Python!')
x = 1 + 1
print(f'Result: {x}')
"""
    tool, _ = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    result = tool(code=code, requirements=None).call()
    assert "Hello from Python!" in result
    assert "Result: 2" in result


def test_execute_python_with_requirements(computer_toolkit: ComputerUseToolkit):
    """Test executing Python code with requirements."""
    code = """
import mirascope
print(mirascope)
"""
    config = ComputerUseToolkitConfig(
        docker_image="python:3.13-slim",
        max_memory="256m",
        allow_network=True,  # To use pip install
    )
    tool, _ = ComputerUseToolkit.from_config(config)().create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    result = tool(code=code, requirements=["mirascope"]).call()
    assert result.startswith("<module 'mirascope' from")


def test_execute_python_with_requirements_invalid_package(
    computer_toolkit: ComputerUseToolkit,
):
    """Test executing Python code with requirements."""
    code = ""
    config = ComputerUseToolkitConfig(
        docker_image="python:3.13-slim",
        max_memory="256m",
        allow_network=True,  # To use pip install
    )
    tool, _ = ComputerUseToolkit.from_config(config)().create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    result = tool(code=code, requirements=["-invalid-"]).call()
    assert result.startswith("Error installing requirements: ")


def test_execute_python_with_requirements_network_disabled(
    computer_toolkit: ComputerUseToolkit,
):
    """Test executing Python code with requirements."""
    code = ""
    tool, _ = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    result = tool(code=code, requirements=["mirascope"]).call()
    assert (
        result
        == "Error: Network access is disabled. Cannot install requirements via pip."
    )


def test_execute_shell(computer_toolkit: ComputerUseToolkit):
    """Test executing shell commands."""
    _, tool = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecuteShell)
    result = tool(command="echo 'Hello from shell!'").call()
    assert "Hello from shell!" in result


def test_container_cleanup(computer_toolkit: ComputerUseToolkit):
    """Test that containers are properly cleaned up."""
    client = docker.from_env()
    initial_containers = len(client.containers.list())

    tool, _ = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    tool(code="print('test')", requirements=None).call()

    # Check that no containers are left running
    assert len(client.containers.list()) == initial_containers


def test_execute_python_with_syntax_error(computer_toolkit: ComputerUseToolkit):
    """Test executing Python code with syntax error."""
    code = """
print('Hello'
x = 1 + 
"""
    tool, _ = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    result = tool(code=code).call()
    assert "SyntaxError" in result


def test_execute_shell_with_error(computer_toolkit: ComputerUseToolkit):
    """Test executing invalid shell command."""
    _, tool = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecuteShell)
    result = tool(command="nonexistent_command").call()
    assert "not found" in result.lower()


def test_container_error_handling(computer_toolkit: ComputerUseToolkit):
    """Test error handling when container operations fail."""
    tool, _ = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    tool_instance = tool(code="print('test')")

    # Force container to stop to simulate error
    container = cast(DockerOperation, tool_instance)._container
    container.stop()

    # Next execution should handle the error and create a new container
    result = tool_instance.call()
    assert "Error executing code:" in result


def test_execute_python_with_file_creation(computer_toolkit: ComputerUseToolkit):
    """Test executing Python code that creates files."""
    code = """
with open('test.txt', 'w') as f:
    f.write('Hello from Python!')
print('File created')
"""
    tool, _ = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    result = tool(code=code).call()
    assert "File created" in result


def test_execute_shell_with_pipe(computer_toolkit: ComputerUseToolkit):
    """Test executing shell commands with pipe."""
    _, tool = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecuteShell)
    result = tool(command="echo 'Hello' | grep 'Hello'").call()
    assert "Hello" in result


def test_container_cleanup_on_error():
    """Test container cleanup when initialization fails."""
    config = ComputerUseToolkitConfig(
        docker_image="nonexistent:latest",  # Invalid image
        max_memory="256m",
        allow_network=False,
    )
    toolkit = ComputerUseToolkit.from_config(config)()
    tool, _ = toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    result = tool(code="print('test')").call()
    assert "Error" in result


def test_docker_operation_del(computer_toolkit: ComputerUseToolkit):
    """Test DockerOperation's __del__ method."""
    tool, _ = computer_toolkit.create_tools()
    assert issubclass(tool, ComputerUseToolkit.ExecutePython)
    tool_instance = tool(code="print('test')")

    # Force container cleanup through __del__
    docker_op = cast(DockerOperation, tool_instance)
    container = docker_op._container
    container_id = cast(str, container.id)

    # Explicitly call __del__
    docker_op.__del__()

    # Verify container is stopped
    client = docker.from_env()
    with pytest.raises(docker.errors.NotFound):  # pyright: ignore [reportAttributeAccessIssue]
        client.containers.get(container_id)


def test_usage_description(computer_toolkit: ComputerUseToolkit):
    """Test usage description."""
    assert (
        computer_toolkit.usage_description()
        == """- Tools for code execution:
    - ExecutePython: Executes Python code with optional requirements in a Docker container
    - ExecuteShell: Executes shell commands in a Docker container"""
    )
