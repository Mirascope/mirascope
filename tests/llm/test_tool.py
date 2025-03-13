from mirascope.core.base.tool import BaseTool
from mirascope.llm.tool import Tool


class DummyTool(BaseTool):
    def call(self):
        return "dummy_tool_call"

    @property
    def model_fields(self):  # pyright: ignore [reportIncompatibleMethodOverride,reportIncompatibleVariableOverride]
        return ["field1"]

    field1: str = "value"


def test_tool():
    dummy_tool_instance = DummyTool()
    tool_instance = Tool(tool=dummy_tool_instance)  # pyright: ignore [reportAbstractUsage]
    assert tool_instance.call() == "dummy_tool_call"
    assert tool_instance.field1 == "value"
