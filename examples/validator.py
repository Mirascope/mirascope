"""A basic example showing how to use field validators to validate the input data.

Note: All validators are defined in the class because updates to the validators will
affect the output of the model.
"""
import os
from typing import Union

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
)

from mirascope import OpenAICallParams, OpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

chat = OpenAIChat()

topic = "baking"


class QuestionPrompt(Prompt):
    """
    SYSTEM:
    You are an expert in {topic}.

    USER:
    {question}
    """

    topic: str = topic
    question: str = Field(..., description="The user's question.")

    call_params = OpenAICallParams(model="gpt-3.5-turbo", temperature=0.1)

    @field_validator("question", mode="after")
    @classmethod
    def validate_question(cls, question: str) -> str:
        class Text(BaseModel):
            is_question: bool = Field(
                ..., description="True if the text is a question. False otherwise."
            )

        class Experience(BaseModel):
            is_experience_relevant: bool = Field(
                ...,
                description=f"True if question is related to {topic}. False otherwise.",
            )

        text = chat.extract(Text, question)
        experience = chat.extract(Experience, question)

        assert text.is_question, f"The text is not a question: {question}"
        assert (
            experience.is_experience_relevant
        ), f"The question is not relevant to {topic}: {question}"

        return question


class HowToGuide(BaseModel):
    steps: Union[list[str], str] = Field(
        ..., description="The steps to perform the task or answer the question."
    )


try:
    content = chat.create(QuestionPrompt(question="cake recipe?"))
    guide = chat.extract(HowToGuide, str(content))
    print(guide)
except ValidationError:
    print("Either the text was not a question or it is not relevant to the topic.")
