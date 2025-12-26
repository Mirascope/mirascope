"""The `FromCallArgs` class annotation for marking a field as a call argument."""

from pydantic.fields import FieldInfo


class FromCallArgs:
    """A marker class for indicating that a field is a call argument.

    This ensures that the LLM call does not attempt to generate this field. Instead, it
    will populate this field with the call argument with a matching name.

    This is useful for colocating e.g. validation of a generated output against and
    input argument (such as the length of an output given a number input).

    Example:

    ```
    class Book(BaseModel):
        title: Annotated[str, llm.formatting.FromCallArgs()]
        author: Annotated[str, llm.formatting.FromCallArgs()]
        summary: str


    @llm.call(
        provider_id="openai",
        model_id="openai/gpt-5-mini",
        format=Book,
    )
    def summarize_book(title: str, author: str):
        return f"Summarize {title} by {author}."
    ```
    """


def is_from_call_args(field: FieldInfo) -> bool:
    """Check if a field has `FromCallArgs` metadata.

    Args:
        field: The Pydantic field to check.

    Returns:
        True if the field is marked with `FromCallArgs`, False otherwise.
    """
    return any(isinstance(m, FromCallArgs) for m in field.metadata)
