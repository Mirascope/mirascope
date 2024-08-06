"""Iterative chaining by feeding the feedback back into the chain."""

import os

from pydantic import BaseModel, Field

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


class SummaryFeedback(BaseModel):
    """Feedback on summary with a critique and review rewrite based on said critique."""

    critique: str = Field(..., description="The critique of the summary.")
    rewritten_summary: str = Field(
        ...,
        description="A rewritten sumary that takes the critique into account.",
    )


@openai.call(model="gpt-4o")
def summarizer(original_text: str):
    """Summarize the following text into one sentence: {original_text}"""


@openai.call(model="gpt-4o", response_model=SummaryFeedback)
def resummarizer(original_text: str, summary: str):
    """
    Original Text: {original_text}
    Summary: {summary}

    Critique the summary of the original text.
    Then rewrite the summary based on the critique. It must be one sentence.
    """


def rewrite_iteratively(original_text: str, summary: str, depth=2):
    feedback = original_text
    for _ in range(depth):
        feedback = resummarizer(original_text=feedback, summary=summary)
    return feedback.rewritten_summary


original_text = """
In the heart of a dense forest, a boy named Timmy pitched his first tent, fumbling with the poles and pegs.
His grandfather, a seasoned camper, guided him patiently, their bond strengthening with each knot tied.
As night fell, they sat by a crackling fire, roasting marshmallows and sharing tales of old adventures.
Timmy marveled at the star-studded sky, feeling a sense of wonder he'd never known.
By morning, the forest had transformed him, instilling a love for the wild that would last a lifetime.
"""

summary = summarizer(original_text=original_text).content
print(f"Summary: {summary}")
# > Summary: In the dense forest, Timmy's first tent-pitching experience with his seasoned camper grandfather deepened their bond and ignited a lifelong love for the wild.
rewritten_summary = rewrite_iteratively(original_text, summary)
print(f"Rewritten Summary: {rewritten_summary}")
# > Rewritten Summary: In the dense forest, Timmy's first tent-pitching experience with his seasoned camper grandfather, filled with roasting marshmallows and sharing tales by the fire, deepened their bond, filled him with wonder at the starry sky, and ignited a lifelong love for the wild.
