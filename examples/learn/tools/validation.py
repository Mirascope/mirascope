from typing import Annotated

from pydantic import AfterValidator, ValidationError

from mirascope.core import BaseTool, openai, prompt_template


def is_upper(v: str) -> str:
    assert v.isupper(), "Must be uppercase"
    return v


class FormatBook(BaseTool):
    title: Annotated[str, AfterValidator(is_upper)]
    author: str

    def call(self) -> str:
        return f"{self.title} by {self.author}"


@openai.call(model="gpt-4", tools=[FormatBook])
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    response = recommend_book("fantasy")
    if tool := response.tool:
        print(tool.call())
    else:
        print(response.content)
except ValidationError as e:
    print(e)
    # > 1 validation error for FormatBook
    #   title
    #     Assertion failed, Must be uppercase [type=assertion_error, input_value='The Name of the Wind', input_type=str]
    #       For further information visit https://errors.pydantic.dev/2.8/v/assertion_error
