"""A basic prompt to solve a math problem."""

from typing import Type

from pydantic import BaseModel, Field

from mirascope import tags
from mirascope.openai import OpenAIExtractor

prev_revision_id = "0002"
revision_id = "0003"


class ProblemDetails(BaseModel):
    solving_steps: str = Field(description="The steps to solve the math problem.")
    answer: int = Field(description="the answer to the math problem.")


@tags(["version:0003"])
class ProblemSolver(OpenAIExtractor[ProblemDetails]):
    extract_schema: Type[ProblemDetails] = ProblemDetails
    prompt_template = """
    Here is a math problem: {problem}
    Write out the answer step by step to arrive at the answer.
    """

    problem: str
