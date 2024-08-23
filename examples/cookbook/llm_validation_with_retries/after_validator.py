from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field, ValidationError

from mirascope.core import anthropic, prompt_template


class SpellingAndGrammarCheck(BaseModel):
    has_errors: bool = Field(
        description="Whether the text has typos or grammatical errors"
    )


@anthropic.call(
    model="claude-3-5-sonnet-20240620",
    response_model=SpellingAndGrammarCheck,
    json_mode=True,
)
@prompt_template(
    """
    Does the following text have any typos or grammatical errors? {text}
    """
)
def check_for_errors(text: str): ...


class TextWithoutErrors(BaseModel):
    text: Annotated[
        str,
        AfterValidator(
            lambda t: t
            if not (check_for_errors(t)).has_errors
            else (_ for _ in ()).throw(ValueError("Text contains errors"))
        ),
    ]


valid = TextWithoutErrors(text="This is a perfectly written sentence.")

try:
    invalid = TextWithoutErrors(
        text="I walkd to supermarket and i picked up some fish?"
    )
except ValidationError as e:
    print(f"Validation error: {e}")
    # > Validation error: 1 validation error for TextWithoutErrors
    #   text
    #     Value error, Text contains errors [type=value_error, input_value='I walkd to supermarket a... i picked up some fish?', input_type=str]
    #       For further information visit https://errors.pydantic.dev/2.8/v/value_error
