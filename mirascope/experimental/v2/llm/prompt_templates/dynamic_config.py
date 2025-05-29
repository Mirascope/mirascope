"""The `DynamicConfig` class for LLM dynamic configuration."""

from collections.abc import Sequence

from typing_extensions import NotRequired, TypedDict

from ..tools import ToolDef
from ..types import Jsonable


class DynamicConfig(TypedDict):
    """Class for specifying dynamic configuration in a prompt template method.

    This class allows prompt template functions to return additional configuration
    options that will be applied during message rendering, such as computed fields
    that should be injected into the template or tools that should be made available
    to the LLM.
    """

    computed_fields: NotRequired[dict[str, Jsonable]]
    """The fields injected into the messages that are computed dynamically.
    
    These fields will be available for use in the template with the {{ field_name }} syntax,
    and will override any fields with the same name provided in the function arguments.
    """

    tools: NotRequired[Sequence[ToolDef]]
    """The list of dynamic tools to merge into the existing tools in the LLM call.
    
    These tools will be added to any tools specified in the call decorator.
    """
