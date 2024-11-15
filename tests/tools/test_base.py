from typing import ClassVar

from pydantic import Field

from mirascope.tools.base import ConfigurableTool, _ConfigurableToolConfig


class MockConfigConfigurable(_ConfigurableToolConfig):
    value: str = Field("default")


class MockTool(ConfigurableTool[MockConfigConfigurable]):
    __configurable_tool_config__ = MockConfigConfigurable()  # pyright: ignore [reportCallIssue]
    __prompt_usage_description__: ClassVar[str] = "Test description"

    input: str = Field(..., description="Test input")

    def call(self) -> str:
        return f"Test output: {self.input}"


def test_tool_config():
    config = MockConfigConfigurable()  # pyright: ignore [reportCallIssue]
    assert config.value == "default"

    custom_config = MockConfigConfigurable(value="custom")
    assert custom_config.value == "custom"

    env_config = MockConfigConfigurable.from_env()
    assert isinstance(env_config, MockConfigConfigurable)


def test_configurable_tool():
    tool = MockTool(input="test")
    result = tool.call()
    assert result == "Test output: test"


def test_tool_config_access():
    tool = MockTool(input="test")
    config = tool._get_config()
    assert isinstance(config, MockConfigConfigurable)
    assert config.value == "default"


def test_configurable_tool_from_config():
    custom_config = MockConfigConfigurable(value="custom")
    CustomTool = MockTool.from_config(custom_config)

    tool = CustomTool(input="test")  # pyright: ignore [reportCallIssue]
    assert isinstance(tool._get_config(), MockConfigConfigurable)
    assert tool._get_config().value == "custom"

    result = tool.call()
    assert result == "Test output: test"
