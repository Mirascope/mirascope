"""Classes for using tools with Anthropic's Claude API."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from json import JSONDecodeError, loads
from textwrap import dedent
from typing import Any, Callable, Type, TypeVar, Union, cast

from pydantic import BaseModel

from ..base import BaseTool, BaseType
from ..base.utils import (
    convert_base_model_to_tool,
    convert_base_type_to_tool,
    convert_function_to_tool,
)

BaseTypeT = TypeVar("BaseTypeT", bound=BaseType)


class AnthropicTool(BaseTool[ET.Element]):
    '''A base class for easy use of tools with the Anthropic Claude client.

    `AnthropicTool` internally handles the logic that allows you to use tools with
    simple calls such as `AnthropicCallResponse.tool` or `AnthropicTool.fn`, as seen in
    the example below.

    Example:

    ```python
    from mirascope import AnthropicCall, AnthropicCallParams


    def animal_matcher(fav_food: str, fav_color: str) -> str:
        """Tells you your most likely favorite animal from personality traits.

        Args:
            fav_food: your favorite food.
            fav_color: your favorite color.

        Returns:
            The animal most likely to be your favorite based on traits.
        """
        return "Your favorite animal is the best one, a frog."


    class AnimalMatcher(AnthropicCall):
        prompt_template = """
        Tell me my favorite animal if my favorite food is {food} and my
        favorite color is {color}.
        """

        food: str
        color: str

        call_params = AnthropicCallParams(tools=[animal_matcher])


    response = AnimalMatcher(food="pizza", color="red").call
    tool = response.tool
    print(tool.fn(**tool.args))
    #> Your favorite animal is the best one, a frog.
    ```
    '''

    @classmethod
    def tool_schema(cls) -> str:
        """Constructs XML tool schema string for use with Anthropic's Claude API."""
        json_schema = super().tool_schema()
        tool_schema = (
            dedent(
                """
                <tool_description>
                <tool_name>{name}</tool_name>
                <description>
                {description}
                </description>
                """
            )
            .strip()
            .format(name=cls.__name__, description=json_schema["description"])
        )

        tool_schema += "\n"
        if "parameters" in json_schema:
            tool_schema += _process_schema(json_schema["parameters"])
        tool_schema += "</tool_description>"
        return tool_schema

    @classmethod
    def from_tool_call(cls, tool_call: ET.Element) -> AnthropicTool:
        """Extracts an instance of the tool constructed from a tool call response.

        Given the `<invoke>...</invoke>` block in a `Message` from an Anthropic call
        response, this method parses out the XML defining the tool call and creates an
        `AnthropicTool` instance from it.

        Args:
            tool_call: The XML `str` from which to extract the tool.

        Returns:
            An instance of the tool constructed from the tool call.

        Raises:
            ValidationError: if the tool call doesn't match the tool schema.
        """

        def _parse_xml_element(element: ET.Element) -> Union[str, dict, list]:
            """Recursively parse an XML element into a Python data structure."""
            children = list(element)
            if not children:
                if element.text:
                    text = element.text.strip().replace("\\n", "").replace("\\", "")
                    # Attempt to load JSON-like strings as Python data structures
                    try:
                        return loads(text)
                    except JSONDecodeError:
                        return text
                else:
                    return ""

            if (
                len(children) > 1
                and all(child.tag == children[0].tag for child in children)
            ) or (
                len(children) == 1
                and (children[0].tag == "entry" or children[0].tag == "item")
            ):
                if children[0].tag == "entry":
                    dict_result = {}
                    for child in children:
                        key, value = child.find("key"), child.find("value")
                        if key is not None and value is not None:
                            dict_result[key.text] = _parse_xml_element(value)
                    return dict_result
                else:
                    return [_parse_xml_element(child) for child in children]

            result: dict[str, Any] = {}
            for child in children:
                child_value = _parse_xml_element(child)
                result[child.tag] = child_value
            return result

        parameters = cast(dict[str, Any], _parse_xml_element(tool_call))
        parameters["tool_call"] = tool_call
        return cls.model_validate(parameters)

    @classmethod
    def from_model(cls, model: Type[BaseModel]) -> Type[AnthropicTool]:
        """Constructs a `AnthropicTool` type from a `BaseModel` type."""
        return convert_base_model_to_tool(model, AnthropicTool)

    @classmethod
    def from_fn(cls, fn: Callable) -> Type[AnthropicTool]:
        """Constructs a `AnthropicTool` type from a function."""
        return convert_function_to_tool(fn, AnthropicTool)

    @classmethod
    def from_base_type(cls, base_type: Type[BaseTypeT]) -> Type[AnthropicTool]:
        """Constructs a `AnthropicTool` type from a `BaseType` type."""
        return convert_base_type_to_tool(base_type, AnthropicTool)


def _process_schema(schema: dict[str, Any]) -> str:
    schema_xml = ""
    if "$defs" in schema:
        schema_xml += "<definitions>\n"
        for def_name, definition in schema["$defs"].items():
            schema_xml += f"<definition name='{def_name}'>\n"
            schema_xml += _process_property(definition)
            schema_xml += "</definition>\n"
        schema_xml += "</definitions>"
    if "properties" in schema:
        schema_xml += "<parameters>\n"
        for prop, definition in schema["properties"].items():
            schema_xml += "<parameter>\n"
            schema_xml += f"<name>{prop}</name>\n"
            schema_xml += _process_property(definition)
            schema_xml += "</parameter>\n"
        schema_xml += "</parameters>\n"
    return schema_xml


# TODO: consider using ET subelements instead of string concat
def _process_property(definition: dict[str, Any]) -> str:
    prop_xml = ""
    prop_type = definition.get("type", "object")

    if "$ref" in definition:
        ref_name = definition["$ref"].split("/")[-1]
        prop_xml += f"<reference name='{ref_name}'/>\n"
    elif prop_type == "array":
        prop_xml += "<type>list</type>\n"
        items_def = None
        if "items" in definition:
            items_def = definition["items"]
        elif "prefixItems" in definition:
            items_def = definition["prefixItems"]
        if items_def:
            if isinstance(items_def, dict):
                prop_xml += "<element_type>\n"
                prop_xml += _process_property(items_def)
                prop_xml += "</element_type>\n"
            else:
                for item in items_def:
                    prop_xml += "<element_type>\n"
                    prop_xml += _process_property(item)
                    prop_xml += "</element_type>\n"
        if "maxItems" in definition:
            prop_xml += f"<maxItems>{definition['maxItems']}</maxItems>\n"
        if "minItems" in definition:
            prop_xml += f"<minItems>{definition['minItems']}</minItems>\n"
        if "uniqueItems" in definition:
            prop_xml += (
                f"<uniqueItems>{str(definition['uniqueItems']).lower()}</uniqueItems>\n"
            )
    elif "enum" in definition:
        prop_xml += "<type>enum</type>\n"
        prop_xml += "<values>\n"
        for value in definition["enum"]:
            prop_xml += f"<value>{value}</value>\n"
        prop_xml += "</values>\n"
        prop_xml += f"<value_type>{prop_type}</value_type>\n"
    elif "anyOf" in definition:
        prop_xml += "<type>union</type>\n"
        prop_xml += "<options>\n"
        for option in definition["anyOf"]:
            prop_xml += "<option>\n"
            prop_xml += _process_property(option)
            prop_xml += "</option>\n"
        prop_xml += "</options>\n"
    elif "const" in definition:
        prop_xml += "<type>literal</type>\n"
        prop_xml += f"<value>{definition['const']}</value>\n"
    elif "additionalProperties" in definition:
        prop_xml += "<type>dictionary</type>\n"
        prop_xml += "<entry>\n"
        prop_xml += "<key>\n<type>string</type>\n</key>\n"
        prop_xml += "<value>\n"
        prop_xml += _process_property(definition["additionalProperties"])
        prop_xml += "</value>\n"
        prop_xml += "</entry>\n"
    elif prop_type in ["string", "number", "integer", "boolean"]:
        prop_xml += f"<type>{prop_type}</type>\n"
    elif prop_type == "null":
        prop_xml += "<type>null</type>\n"
    else:
        prop_xml += "<type>object</type>\n"
        prop_xml += _process_schema(definition)

    if "description" in definition:
        prop_xml += f"<description>{definition['description']}</description>\n"
    if "default" in definition:
        default_value = definition["default"]
        if default_value is None:
            prop_xml += "<default>null</default>\n"
        else:
            prop_xml += f"<default>{default_value}</default>\n"

    return prop_xml
