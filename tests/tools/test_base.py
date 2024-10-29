from typing import ClassVar

from pydantic import BaseModel, Field

from mirascope.tools.base import ConfigurableTool, _ToolConfig


class MockSchema(BaseModel):
    value: str


class MockConfig(_ToolConfig):
    value: str = Field("default")

    @classmethod
    def from_env(cls) -> _ToolConfig:
        return cls() # pyright: ignore [reportCallIssue]


class MockTool(ConfigurableTool[MockConfig, MockSchema]):
    __config__ = MockConfig() # pyright: ignore [reportCallIssue]
    __prompt_usage_description__: ClassVar[str] = "Test description"

    input: str = Field(..., description="Test input")

    def call(self) -> MockSchema:
        return MockSchema(value=f"Test output: {self.input}")

    @classmethod
    def _name(cls) -> str:
        return "test_tool"

    @classmethod
    def _description(cls) -> str:
        return "Test tool description"


def test_tool_config():
    config = MockConfig() # pyright: ignore [reportCallIssue]
    assert config.value == "default"

    custom_config = MockConfig(value="custom")
    assert custom_config.value == "custom"

    env_config = MockConfig.from_env()
    assert isinstance(env_config, MockConfig)




def test_configurable_tool():
    tool = MockTool(input="test")
    result = tool.call()
    assert isinstance(result, MockSchema)
    assert result.value == "Test output: test"


def test_tool_config_access():
    tool = MockTool(input="test")
    config = tool._config()
    assert isinstance(config, MockConfig)
    assert config.value == "default"


def test_configurable_tool_from_config():
    custom_config = MockConfig(value="custom")
    CustomTool = MockTool.from_config(custom_config)

    tool = CustomTool(input="test") # pyright: ignore [reportCallIssue]
    assert isinstance(tool._config(), MockConfig)
    assert tool._config().value == "custom"

    result = tool.call()
    assert isinstance(result, MockSchema)
    assert result.value == "Test output: test"
