"""
A basic example showing how to use field validators to validate the input data.

Note: All validators are defined in the class because updates to the validators will
affect the output of the model.
"""

import os
from typing import Annotated, Type, Union

from pydantic import AfterValidator, BaseModel, Field, ValidationError

from mirascope.openai import OpenAICall, OpenAICallParams, OpenAIExtractor

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

topic = "baking"


class ValidationInfo(BaseModel):
    is_question: bool = Field(
        ..., description="True if the text is a question. False otherwise."
    )
    is_experience_relevant: bool = Field(
        ...,
        description=f"True if question is related to {topic}. False otherwise.",
    )


class Validator(OpenAIExtractor[ValidationInfo]):
    extract_schema: Type[ValidationInfo] = ValidationInfo
    prompt_template = "{question}"

    question: str


def validate_question(question: str) -> str:
    """Validates the input question."""

    info = Validator(question=question).extract()

    assert info.is_question, f"The text is not a question: {question}"
    assert (
        info.is_experience_relevant
    ), f"The question is not relevant to {topic}: {question}"

    return question


class Expert(OpenAICall):
    prompt_template = """
    SYSTEM: You are an expert in {topic}.
    USER: {question}
    """

    topic: str = topic
    question: Annotated[str, AfterValidator(validate_question)] = Field(
        ..., description="The user's question."
    )

    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125", temperature=0.1)


class HowToGuide(BaseModel):
    """A how-to guide for the user's question."""

    steps: Union[list[str], str] = Field(
        ..., description="The steps to perform the task or answer the question."
    )


class Guide(OpenAIExtractor[HowToGuide]):
    extract_schema: Type[HowToGuide] = HowToGuide
    prompt_template = "{content}"

    content: str


try:
    response = Expert(question="cake recipe?").call()
    guide = Guide(content=response.content).extract()
    print(guide)
except ValidationError as e:
    print(e)
    # Example: The text is not a question: cake recipe
    # Example: The question is not relevant to baking: how to play guitar
