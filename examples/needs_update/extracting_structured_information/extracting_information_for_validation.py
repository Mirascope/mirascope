"""
A basic example showing how to use field validators to validate the input data.

Note: All validators are defined in the class because updates to the validators will
affect the output of the model.
"""

import os
from typing import Annotated, Union

from pydantic import AfterValidator, BaseModel, Field, ValidationError, validate_call

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"

topic = "baking"


class ValidationInfo(BaseModel):
    is_question: bool = Field(
        ..., description="True if the text is a question. False otherwise."
    )
    is_experience_relevant: bool = Field(
        ...,
        description=f"True if question is related to {topic}. False otherwise.",
    )


@openai.call(model="gpt-4o", response_model=ValidationInfo)
def validator(question: str):
    """{question}"""


def validate_question(question: str) -> str:
    """Validates the input question."""

    info = validator(question=question)

    assert info.is_question, f"The text is not a question: {question}"
    assert (
        info.is_experience_relevant
    ), f"The question is not relevant to {topic}: {question}"

    return question


@openai.call(model="gpt-3.5-turbo-0125", temperature=0.1)
@validate_call
def expert(topic: str, question: Annotated[str, AfterValidator(validate_question)]):
    """
    SYSTEM: You are an expert in {topic}.
    USER: {question}
    """


class HowToGuide(BaseModel):
    """A how-to guide for the user's question."""

    steps: Union[list[str], str] = Field(
        ..., description="The steps to perform the task or answer the question."
    )


@openai.call(model="gpt-4o", response_model=HowToGuide)
def guide(content: str):
    """{content}"""


try:
    response = expert(topic=topic, question="cake recipe?")
    guide_content = guide(content=response.content)
    print(guide_content)
except ValidationError as e:
    print(e)
    # Example: The text is not a question: cake recipe
    # Example: The question is not relevant to baking: how to play guitar
