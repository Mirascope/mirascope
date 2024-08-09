from typing import Annotated

from dotenv import load_dotenv
from pydantic import AfterValidator, BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt

from mirascope.core import anthropic, prompt_template
from mirascope.integrations.tenacity import collect_errors

load_dotenv()


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


class GrammarCheck(BaseModel):
    text: Annotated[
        str,
        AfterValidator(
            lambda t: t
            if not (check_for_errors(t)).has_errors
            else (_ for _ in ()).throw(ValueError("Text still contains errors"))
        ),
    ] = Field(description="The corrected text with proper grammar")
    explanation: str = Field(description="Explanation of the corrections made")


@retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
@anthropic.call(
    "claude-3-5-sonnet-20240620", response_model=GrammarCheck, json_mode=True
)
@prompt_template(
    """
    {previous_errors}

    Correct the grammar in the following text.
    If no corrections are needed, return the original text.
    Provide an explanation of any corrections made.

    Text: {text}
    """
)
def correct_grammar(
    text: str, *, errors: list[ValidationError] | None = None
) -> anthropic.AnthropicDynamicConfig:
    previous_errors = f"Previous Errors: {errors}" if errors else "No previous errors."
    return {"computed_fields": {"previous_errors": previous_errors}}


try:
    text = "I has went to the store yesterday and buyed some milk."
    result = correct_grammar(text)
    print(f"Corrected text: {result.text}")
    print(f"Explanation: {result.explanation}")
except ValidationError:
    print("Failed to correct grammar after 3 attempts")
