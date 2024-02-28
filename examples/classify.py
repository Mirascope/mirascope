import enum
import os

from pydantic import BaseModel

from mirascope import OpenAIChat

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class Label(str, enum.Enum):
    STATEMENT = "statement"
    QUESTION = "question"
    AGGRESSIVE = "aggressive"
    NEUTRAL = "neutral"
    NICE = "nice"


class TextLabels(BaseModel):
    """A model for labels about some speech."""

    labels: list[Label]


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
    print(text_info.labels)

    # Output:

    # text: "Hey buddy, want to grab lunch tomorrow?"
    # [<Label.QUESTION: 'question'>, <Label.NICE: 'nice'>]

    # text: "You will pay for what you have done, you pathetic loser."
    # [<Label.AGGRESSIVE: 'aggressive'>, <Label.STATEMENT: 'statement'>]
