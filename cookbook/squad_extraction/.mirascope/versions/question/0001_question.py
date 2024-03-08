"""A prompt for asking a question about a paragraph of text.

{
  "exact": 79.3103448275862,
  "f1": 89.4777077966733,
  "total": 116,
  "HasAns_exact": 79.3103448275862,
  "HasAns_f1": 89.4777077966733,
  "HasAns_total": 116
}
"""

from pydantic import BaseModel

from mirascope.base import tags
from mirascope.openai import OpenAICallParams, OpenAIPrompt

prev_revision_id = "None"
revision_id = "0001"


class ExtractedAnswer(BaseModel):
    """The answer to a question about a paragraph of text."""

    answer: str


@tags(["version:0001"])
class QuestionPrompt(OpenAIPrompt):
    """
    Paragraph: {paragraph}

    Question: {question}
    """

    paragraph: str
    question: str

    call_params = OpenAICallParams(model="gpt-3.5-turbo-1106")
