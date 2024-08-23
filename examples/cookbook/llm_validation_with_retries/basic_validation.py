from pydantic import BaseModel, Field

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


text = "Yestday I had a gret time!"
response = check_for_errors(text)
assert response.has_errors
