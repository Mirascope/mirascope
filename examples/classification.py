import enum
import os
from typing import Type

from pydantic import BaseModel

from mirascope.openai import OpenAIExtractor

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class Label(str, enum.Enum):
    STATEMENT = "statement"
    QUESTION = "question"
    AGGRESSIVE = "aggressive"
    NEUTRAL = "neutral"
    NICE = "nice"


class TextLabels(BaseModel):
    """A model for labels about some speech."""

    labels: list[Label]


class LabelsExtractor(OpenAIExtractor[TextLabels]):
    extract_schema: Type[TextLabels] = TextLabels
    prompt_template = "{text}"

    text: str


for extractor in [
    LabelsExtractor(text="Hey buddy, want to grab lunch tomorrow?"),
    LabelsExtractor(text="You will pay for what you have done, you pathetic loser."),
]:
    print(extractor.extract(retries=5))

    # Output:

    # text: "Hey buddy, want to grab lunch tomorrow?"
    # [<Label.QUESTION: 'question'>, <Label.NICE: 'nice'>]

    # text: "You will pay for what you have done, you pathetic loser."
    # [<Label.AGGRESSIVE: 'aggressive'>, <Label.STATEMENT: 'statement'>]
