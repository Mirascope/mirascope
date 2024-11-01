import docker
import pytest

from mirascope.tools import ComputerUseToolkit, ComputerUseToolkitConfig


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
