import enum
import os
from typing import List

from pydantic import BaseModel

from mirascope import OpenAIChat

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class Labels(str, enum.Enum):
    STATEMENT = "statement"
    QUESTION = "question"
    AGGRESSIVE = "aggressive"
    NEUTRAL = "neutral"
    NICE = "nice"


class TextLabels(BaseModel):
    """A model for labels about some speech."""

    labels: List[Labels]


chat = OpenAIChat(model="gpt-3.5-turbo-1106")
texts = [
    "Hey buddy, want to grab lunch tomorrow?",
    "You will pay for what you have done, you pathetic loser.",
]
for text in texts:
    text_info = chat.extract(
        TextLabels,
        text,
        retries=5,
    )
    print(text_info)

    # Output:

    # text: "Hey buddy, want to grab lunch tomorrow?"
    # labels=[<Labels.QUESTION: 'question'>, <Labels.NICE: 'nice'>]

    # text: "You will pay for what you have done, you pathetic loser."
    # labels=[<Labels.AGGRESSIVE: 'aggressive'>, <Labels.STATEMENT: 'statement'>]
