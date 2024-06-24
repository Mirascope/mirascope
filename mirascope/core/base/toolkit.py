"""The module for defining the toolkit class for LLM call tools."""

from __future__ import annotations

import inspect
from abc import ABC
from typing import Callable, ClassVar, NamedTuple

from pydantic import BaseModel, ConfigDict
from typing_extensions import Concatenate, ParamSpec

from . import BaseTool
from ._utils import convert_function_to_base_tool, get_template_variables

_TOOLKIT_TOOL_METHOD_MARKER: str = "__toolkit_tool_method__"

_namespaces: set[str] = set()

P = ParamSpec("P")


def toolkit_tool(
    method: Callable[Concatenate[BaseToolKit, P], str],
) -> Callable[Concatenate[BaseToolKit, P], str]:
    # Mark the method as a toolkit tool
    setattr(method, _TOOLKIT_TOOL_METHOD_MARKER, True)

    return method


class ToolKitToolMethod(NamedTuple):
    method: Callable[..., str]
    template_vars: list[str]
    template: str


class BaseToolKit(BaseModel, ABC):
    """A class for defining tools for LLM call tools.

    The class should have methods decorated with `@toolkit_tool` to create tools.

    Example:
    ```python
    from mirascope.core.base import BaseToolKit, toolkit_tool
    from mirascope.core import openai

    class BookRecommendationToolKit(BaseToolKit):
        '''A toolkit for recommending books.'''

        __namespace__: ClassVar[str | None] = 'book_tools'
        reading_level: Literal["beginner", "advanced"]

        @toolkit_tool
        def format_book(self, title: str, author: str) -> str:
            '''Returns the title and author of a book nicely formatted.

            Reading level: {self.reading_level}
            '''
            return f"{title} by {author}"

    @openai.call(model="gpt-4o")
    def recommend_book(genre: str, reading_level: Literal["beginner", "advanced"]):
        '''Recommend a {genre} book.'''
        toolkit = BookRecommendationToolKit(reading_level=reading_level)
        return {"tools": toolkit.create_tools()}

    response = recommend_book("fantasy", "beginner")
    if tool := response.tool:
        output = tool.call()
        print(output)
        #> The Name of the Wind by Patrick Rothfuss
    else:
        print(response.content)
        #> Sure! I would recommend...
    ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    _toolkit_tool_methods: ClassVar[list[ToolKitToolMethod]]
    __namespace__: ClassVar[str | None] = None

    def create_tools(self) -> list[type[BaseTool]]:
        """The method to create the tools."""
        return [
            convert_function_to_base_tool(
                method, BaseTool, template.format(self=self), self.__namespace__
            )
            for method, template_vars, template in self._toolkit_tool_methods
        ]

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        # validate the namespace
        if cls.__namespace__:
            if cls.__namespace__ in _namespaces:
                raise ValueError(f"The namespace {cls.__namespace__} is already used")
            _namespaces.add(cls.__namespace__)

        cls._toolkit_tool_methods = []
        for attr in cls.__dict__.values():
            if not getattr(attr, _TOOLKIT_TOOL_METHOD_MARKER, False):
                continue
            # Validate the toolkit_tool_method
            if (template := attr.__doc__) is None:
                raise ValueError("The toolkit_tool method must have a docstring")

            dedented_template = inspect.cleandoc(template)
            template_vars = get_template_variables(dedented_template)

            for var in template_vars:
                if not var.startswith("self."):
                    raise ValueError(
                        "The toolkit_tool method must use self. prefix in template variables "
                        "when creating tools dynamically"
                    )

                self_var = var[5:]

                # Expecting pydantic model fields or class attribute and property
                if self_var in cls.model_fields or hasattr(cls, self_var):
                    continue
                raise ValueError(
                    f"The toolkit_tool method template variable {var} is not found in the class"
                )

            cls._toolkit_tool_methods.append(
                ToolKitToolMethod(attr, template_vars, dedented_template)
            )
        if not cls._toolkit_tool_methods:
            raise ValueError("No toolkit_tool method found")
