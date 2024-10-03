import inspect
from collections.abc import Callable

from pydantic import BaseModel


class FromCallArgs:
    """
    If you want to pass the function arguments to the response model, you can use this metadata.

    example:
    ```python
    class Emotions(BaseModel):
    sentences: Annotated[list[str], FromCallArgs()]
    emotions: list[str]

    @model_validator(mode="after")
    def validate_output_length(self) -> Self:
        if len(self.sentences) != len(self.emotions):
            raise ValueError("length mismatch...")
        return self

    @openai.call(... same as before ..., response_model=Emotions)
    @prompt_template(... same as before ...)
    def classify_emotions(sentences: list[str]): ...
    ```
    """

    pass


def get_call_args_field_names_and_validate(
    response_model: object, fn: Callable
) -> set[str]:
    if not (inspect.isclass(response_model) and issubclass(response_model, BaseModel)):
        return set()
    call_args_fields = _get_call_args_field_names(response_model)
    _validate_call_args(fn, call_args_fields)
    return call_args_fields


def _get_call_args_field_names(response_model: type[BaseModel]) -> set[str]:
    """
    This function is used to get the field names that are marked with the `FromCallArgs` metadata.
    The function doesn't treat the nested fields such like lists or dictionaries.
    """

    exclude_fields: set[str] = set()
    for field_name, field in response_model.model_fields.items():
        if any(isinstance(m, FromCallArgs) for m in field.metadata):
            exclude_fields.add(field_name)
    return exclude_fields


def _validate_call_args(fn: Callable, call_args_fields: set[str]) -> None:
    if not call_args_fields:
        return None
    signature = inspect.signature(fn)
    arguments = signature.parameters.keys()
    if call_args_fields.issubset(arguments):
        return None
    raise ValueError(
        f"The function arguments do not contain all the fields marked with `FromCallArgs`. {arguments=}, {call_args_fields=}"
    )
