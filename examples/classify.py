import enum
import os

from pydantic import BaseModel

from mirascope.openai import OpenAIPrompt

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


class NicePrompt(OpenAIPrompt):
    """Hey buddy, want to grab lunch tomorrow?"""


class MeanPrompt(OpenAIPrompt):
    """You will pay for what you have done, you pathetic loser."""


for prompt in [NicePrompt(), MeanPrompt()]:
    print(prompt.extract(TextLabels, retries=5))

    # Output:

    # text: "Hey buddy, want to grab lunch tomorrow?"
    # [<Label.QUESTION: 'question'>, <Label.NICE: 'nice'>]

    # text: "You will pay for what you have done, you pathetic loser."
    # [<Label.AGGRESSIVE: 'aggressive'>, <Label.STATEMENT: 'statement'>]
