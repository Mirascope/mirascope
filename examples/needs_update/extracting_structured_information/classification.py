"""An example of classifying text using openai.call to extract structured information."""

import enum
import os

from pydantic import BaseModel

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


class Label(str, enum.Enum):
    STATEMENT = "statement"
    QUESTION = "question"
    AGGRESSIVE = "aggressive"
    NEUTRAL = "neutral"
    NICE = "nice"


class TextLabels(BaseModel):
    """A model for labels about some speech."""

    labels: list[Label]


@openai.call(model="gpt-4o", response_model=TextLabels)
def labels_extractor(text: str):
    """{text}"""


for text in [
    "Hey buddy, want to grab lunch tomorrow",
    "You will pay for what you have done, you pathetic loser.",
]:
    print(labels_extractor(text=text))

    # Output:

    # text: "Hey buddy, want to grab lunch tomorrow?"
    # [<Label.QUESTION: 'question'>, <Label.NICE: 'nice'>]

    # text: "You will pay for what you have done, you pathetic loser."
    # [<Label.AGGRESSIVE: 'aggressive'>, <Label.STATEMENT: 'statement'>]
