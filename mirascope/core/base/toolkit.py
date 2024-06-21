from __future__ import annotations

from abc import ABC
from textwrap import dedent
from typing import Callable, Optional, ClassVar, ParamSpec

from pydantic import BaseModel, ConfigDict
from typing_extensions import LiteralString

from . import BaseTool
from ._utils import convert_function_to_base_tool, get_template_variables

_TOOLKIT_TOOL_METHOD_MARKER: LiteralString = "__toolkit_tool_method__"

P = ParamSpec("P")


def toolkit_tool(
        method: Callable[[BaseToolKit, ...], str],
) -> Callable[[BaseToolKit, ...], str]:
    # Mark the method as a toolkit tool
    setattr(method, _TOOLKIT_TOOL_METHOD_MARKER, True)

    return method


class BaseToolKit(BaseModel, ABC):
    """A class for defining tools for LLM call tools."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    _toolkit_tool_method: ClassVar[Callable[[BaseToolKit, ...], str]]
    _toolkit_template_vars: ClassVar[list[str]]

    def create_tool(self) -> type[BaseTool]:
        """The method to create the tools."""
        formated_template = self._toolkit_tool_method.__doc__.format(self=self)
        return convert_function_to_base_tool(self._toolkit_tool_method, BaseTool, formated_template)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        toolkit_tool_method: Optional[Callable] = None
        for name, value in cls.__dict__.items():
            if getattr(value, _TOOLKIT_TOOL_METHOD_MARKER, False):
                if toolkit_tool_method:
                    raise ValueError("Only one toolkit_tool method is allowed")
                toolkit_tool_method = value
        if not toolkit_tool_method:
            raise ValueError("No toolkit_tool method found")

        # Validate the toolkit_tool_method
        if (template := toolkit_tool_method.__doc__) is None:
            raise ValueError("The toolkit_tool method must have a docstring")

        dedented_template = dedent(template).strip()
        if not (template_vars := get_template_variables(dedented_template)):
            raise ValueError("The toolkit_tool method must have template variables")

        if dedented_template != template:
            toolkit_tool_method.__doc__ = dedented_template
        for var in template_vars:
            if not var.startswith("self."):
                # Should be supported un-self variables?
                raise ValueError(
                    "The toolkit_tool method must use self. prefix in template variables"
                )

            self_var = var[5:]
            # Expecting pydantic model fields or class attribute and property
            if self_var in cls.model_fields or hasattr(cls, self_var):
                continue
            raise ValueError(
                f"The toolkit_tool method template variable {var} is not found in the class"
            )

        cls._toolkit_tool_method = toolkit_tool_method
        cls._toolkit_template_vars = template_vars
