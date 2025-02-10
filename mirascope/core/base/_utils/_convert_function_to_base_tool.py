import inspect
from abc import update_abstractmethods
from collections.abc import Callable
from typing import Any, TypeVar, cast, get_type_hints

import jiter
from docstring_parser import Docstring, DocstringMeta, compose, parse
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from ._default_tool_docstring import DEFAULT_TOOL_DOCSTRING

BaseToolT = TypeVar("BaseToolT", bound=BaseModel)


def convert_function_to_base_tool(
    fn: Callable,
    base: type[BaseToolT],
    __doc__: str | None = None,
    __namespace__: str | None = None,
) -> type[BaseToolT]:
    """Constructs a `BaseToolT` type from the given function.

    This method expects all function parameters to be properly documented in identical
    order with identical variable names, as well as descriptions of each parameter.
    Errors will be raised if any of these conditions are not met.

    Args:
        fn: The function to convert.
        base: The `BaseToolT` type to which the function is converted.
        __doc__: The docstring to use for the constructed `BaseToolT` type.
        __namespace__: The namespace to use for the constructed `BaseToolT` type.

    Returns:
        The constructed `BaseToolT` type.

    Raises:
        ValueError: if the given function's parameters don't have type annotations.
        ValueError: if a given function's parameter is in the docstring args section but
            the name doesn't match the docstring's parameter name.
        ValueError: if a given function's parameter is in the docstring args section but
            doesn't have a docstring description.
    """
    docstring, examples = None, []
    func_doc = __doc__ or fn.__doc__
    if func_doc:
        docstring = parse(func_doc)
        for example in docstring.examples or []:
            if example.description:
                examples.append(jiter.from_json(example.description.encode()))
        cleaned_docstring = Docstring(style=docstring.style)
        cleaned_docstring.short_description = docstring.short_description
        cleaned_docstring.blank_after_short_description = (
            docstring.blank_after_short_description
        )
        cleaned_docstring.long_description = docstring.long_description
        cleaned_docstring.blank_after_long_description = (
            docstring.blank_after_long_description
        )
        cleaned_docstring.meta = cast(
            list[DocstringMeta], docstring.many_returns + docstring.raises
        )
        func_doc = compose(cleaned_docstring)

    field_definitions = {}
    hints = get_type_hints(fn, include_extras=True)
    has_self = False
    for i, parameter in enumerate(inspect.signature(fn).parameters.values()):
        if parameter.name == "self":
            has_self = True
            continue
        if parameter.name == "cls":
            continue
        if parameter.annotation == inspect.Parameter.empty:
            raise ValueError("All parameters must have a type annotation.")

        docstring_description = None
        if docstring and i < len(docstring.params):
            docstring_param = docstring.params[i]
            if docstring_param.arg_name != parameter.name:
                raise ValueError(
                    f"Function parameter name {parameter.name} does not match docstring "
                    f"parameter name {docstring_param.arg_name}. Make sure that the "
                    "parameter names match exactly."
                )
            if not docstring_param.description:
                raise ValueError("All parameters must have a description.")
            docstring_description = docstring_param.description

        field_info = FieldInfo(annotation=hints[parameter.name])
        if parameter.default != inspect.Parameter.empty:
            field_info.default = parameter.default
        if docstring_description:  # we check falsy here because this comes from docstr
            field_info.description = docstring_description

        param_name = parameter.name
        if param_name.startswith("model_"):  # model_ is a BaseModel reserved namespace
            param_name = "aliased_" + param_name
            field_info.alias = parameter.name
            field_info.validation_alias = parameter.name
            field_info.serialization_alias = parameter.name

        field_definitions[param_name] = (
            hints[parameter.name],
            field_info,
        )

    model = create_model(
        f"{__namespace__}_{fn.__name__}" if __namespace__ else fn.__name__,
        __base__=base,
        __doc__=inspect.cleandoc(func_doc) if func_doc else DEFAULT_TOOL_DOCSTRING,
        **cast(dict[str, Any], field_definitions),
    )
    if examples:
        model.model_config["json_schema_extra"] = {"examples": examples}

    def call(self: base) -> Any:  # pyright: ignore [reportInvalidTypeForm] # noqa: ANN401
        return fn(
            **(
                ({"self": self} if has_self else {})
                | {
                    str(
                        self.model_fields[field_name].alias
                        if self.model_fields[field_name].alias
                        else field_name
                    ): getattr(self, field_name)
                    for field_name in self.model_dump(exclude={"tool_call", "delta"})
                }
            )
        )

    async def call_async(self: base) -> Callable:  # pyright: ignore [reportInvalidTypeForm]
        return await call(self)

    if inspect.iscoroutinefunction(fn):
        model.call = call_async  # pyright: ignore [reportAttributeAccessIssue]
    else:
        model.call = call  # pyright: ignore [reportAttributeAccessIssue]
    return update_abstractmethods(model)
