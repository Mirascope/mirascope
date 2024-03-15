"""A prompt for asking a question about a paragraph of text.

{
  "exact": 85.34482758620689,
  "f1": 91.55579573683022,
  "total": 116,
  "HasAns_exact": 85.34482758620689,
  "HasAns_f1": 91.55579573683022,
  "HasAns_total": 116
}
"""
from typing import Type

from pydantic import BaseModel, Field

from mirascope.openai import OpenAIExtractor

prev_revision_id = None
revision_id = "0001"


class Answer(BaseModel):
    """The answer to a question about a paragraph of text."""

    answer: str = Field(
        ...,
        description=(
            "The extracted answer to the question. This answer is as concise as "
            "possible, most often just a single word. It is also an exact text match "
            "with text in the provided context."
        ),
    )


class Answerer(OpenAIExtractor[Answer]):
    extract_schema: Type[Answer] = Answer
    prompt_template = """
    SYSTEM:
    You will be asked a question after you read a paragraph. Your task is to
    answer the question based on the information in the paragraph. Your answer
    should be an exact text match to text from the paragraph. Your answer should
    also be one or two words at most is possible.

    USER:
    {paragraph}

    USER:
    {question}
    """

    paragraph: str
    question: str
