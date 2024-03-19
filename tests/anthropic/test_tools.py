"""Tests for the `mirascope.gemini.tools` module."""
import xml.etree.ElementTree as ET
from textwrap import dedent
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from mirascope.anthropic.tools import AnthropicTool
from mirascope.base.tools import DEFAULT_TOOL_DOCSTRING


class FieldDescription(AnthropicTool):
    param: str = Field("default", description="param description")


def test_anthropic_tool_with_description():
    """Tests `AnthropicTool.tool_schema` class method."""
    print(FieldDescription.tool_schema())
    assert FieldDescription.tool_schema() == dedent(
        """
    <tool_description>
    <tool_name>FieldDescription</tool_name>
    <description>
    {description}
    </description>
    <parameters>
    <parameter>
    <name>param</name>
    <type>string</type>
    <description>param description</description>
    <default>default</default>
    </parameter>
    </parameters>
    </tool_description>
            """
    ).strip().format(description=DEFAULT_TOOL_DOCSTRING)


def fake_tool(param: str):
    """A test tool.

    Args:
        param: A test parameter.
    """
    return param


class FakeTool(AnthropicTool):
    """A test tool."""

    param: str = Field(..., description="A test parameter.")


def test_tool_from_fn() -> None:
    """Tests converting a function into a `AnthropicTool`."""
    fake_tool("param")
    assert (
        AnthropicTool.from_fn(fake_tool).model_json_schema()
        == FakeTool.model_json_schema()
    )


def test_tool_from_model() -> None:
    """Tests creating a `AnthropicTool` type from a `BaseModel`."""

    class MyModel(BaseModel):
        """My model"""

        param: str

    tool_type = AnthropicTool.from_model(MyModel)
    assert tool_type.model_json_schema() == MyModel.model_json_schema()


def test_tool_from_base_type() -> None:
    """Tests creating a `AnthropicTool` type from a `BaseModel`."""

    class Str(BaseModel):
        __doc__ = DEFAULT_TOOL_DOCSTRING

        value: str

    assert (
        AnthropicTool.from_base_type(str).model_json_schema() == Str.model_json_schema()
    )


class MyTool(AnthropicTool):
    param1: str
    param2: int
    param3: list[str]
    param4: dict[str, str]
    param5: tuple[str, str]
    param6: set[str]
    param7: Union[str, int]
    param8: Literal["constant"]
    param9: Literal["multiple", "literal", "constants"]
    param10: Optional[str] = None


def test_parse_xml_element() -> None:
    """Tests parsing XML elements into Python data structures."""
    xml_str = """
        <parameters>
            <param1>value1</param1>
            <param2>42</param2>
            <param3>
                <item>item1</item>
                <item>item2</item>
            </param3>
            <param4>
                <entry>
                    <key>key1</key>
                    <value>value1</value>
                </entry>
                <entry>
                    <key>key2</key>
                    <value>value2</value>
                </entry>
            </param4>
            <param5>
                <item>item1</item>
                <item>item2</item>
            </param5>
            <param6>
                <item>item1</item>
                <item>item2</item>
            </param6>
            <param7></param7>
            <param8>
                constant
            </param8>
            <param9>
                literal
            </param9>
            <param10>
                null
            </param10>
        </parameters>
    """
    tool = MyTool.from_tool_call(ET.fromstring(xml_str))
    assert tool.model_dump(exclude={"tool_call"}) == {
        "param1": "value1",
        "param2": 42,
        "param3": ["item1", "item2"],
        "param4": {"key1": "value1", "key2": "value2"},
        "param5": ("item1", "item2"),
        "param6": {"item1", "item2"},
        "param7": "",
        "param8": "constant",
        "param9": "literal",
        "param10": None,
    }


def test_process_schema_and_property() -> None:
    """Tests processing JSON schema into XML schema."""

    xml_schema = MyTool.tool_schema()

    assert (
        xml_schema
        == dedent(
            """
        <tool_description>
        <tool_name>MyTool</tool_name>
        <description>
        Correctly formatted and typed parameters extracted from the completion. Must include required parameters and may exclude optional parameters unless present in the text.
        </description>
        <parameters>
        <parameter>
        <name>param1</name>
        <type>string</type>
        </parameter>
        <parameter>
        <name>param2</name>
        <type>integer</type>
        </parameter>
        <parameter>
        <name>param3</name>
        <type>list</type>
        <element_type>
        <type>string</type>
        </element_type>
        </parameter>
        <parameter>
        <name>param4</name>
        <type>dictionary</type>
        <entry>
        <key>
        <type>string</type>
        </key>
        <value>
        <type>string</type>
        </value>
        </entry>
        </parameter>
        <parameter>
        <name>param5</name>
        <type>list</type>
        <element_type>
        <type>string</type>
        </element_type>
        <element_type>
        <type>string</type>
        </element_type>
        <maxItems>2</maxItems>
        <minItems>2</minItems>
        </parameter>
        <parameter>
        <name>param6</name>
        <type>list</type>
        <element_type>
        <type>string</type>
        </element_type>
        <uniqueItems>true</uniqueItems>
        </parameter>
        <parameter>
        <name>param7</name>
        <type>union</type>
        <options>
        <option>
        <type>string</type>
        </option>
        <option>
        <type>integer</type>
        </option>
        </options>
        </parameter>
        <parameter>
        <name>param8</name>
        <type>literal</type>
        <value>constant</value>
        </parameter>
        <parameter>
        <name>param9</name>
        <type>enum</type>
        <values>
        <value>multiple</value>
        <value>literal</value>
        <value>constants</value>
        </values>
        <value_type>string</value_type>
        </parameter>
        <parameter>
        <name>param10</name>
        <type>union</type>
        <options>
        <option>
        <type>string</type>
        </option>
        <option>
        <type>null</type>
        </option>
        </options>
        <default>null</default>
        </parameter>
        </parameters>
        </tool_description>
    """
        ).strip()
    )


class Reference(BaseModel):
    reference: str


class RefTool(AnthropicTool):
    literal: Literal["value1", "value2"]
    union: Union[str, int, None]
    ref: Reference


def test_schema_types() -> None:
    """Tests handling different JSON schema types."""

    xml_schema = RefTool.tool_schema()

    assert (
        "<definition name='Reference'>\n<type>object</type>\n<parameters>\n<parameter>"
        "\n<name>reference</name>\n<type>string</type>\n</parameter>\n</parameters>"
        "\n</definition>" in xml_schema
    )
    assert "<name>literal</name>" in xml_schema
    assert "<type>enum</type>" in xml_schema
    assert "<values>" in xml_schema
    assert "<value>value1</value>" in xml_schema
    assert "<value>value2</value>" in xml_schema
    assert "<name>union</name>" in xml_schema
    assert "<type>union</type>" in xml_schema
    assert "<options>" in xml_schema
    assert "<type>string</type>" in xml_schema
    assert "<type>integer</type>" in xml_schema
    assert "<type>null</type>" in xml_schema
    assert "<name>ref</name>" in xml_schema
    assert "<reference name='Reference'/>" in xml_schema
