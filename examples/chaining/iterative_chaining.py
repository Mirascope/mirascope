from pydantic import BaseModel, Field

from mirascope.openai import OpenAICall, OpenAIExtractor


class SummaryFeedback(BaseModel):
    """Feedback on summary with a critique and review rewrite based on said critique."""

    critique: str = Field(..., description="The critique of the summary.")
    rewritten_summary: str = Field(
        ...,
        description="A rewritten sumary that takes the critique into account.",
    )


class Summarizer(OpenAICall):
    prompt_template = "Summarize the following text into one sentence: {original_text}"

    original_text: str


class Resummarizer(OpenAIExtractor[SummaryFeedback]):
    extract_schema: type[SummaryFeedback] = SummaryFeedback
    prompt_template = """
    Original Text: {original_text}
    Summary: {summary}

    Critique the summary of the original text.
    Then rewrite the summary based on the critique. It must be one sentence.
    """

    original_text: str
    summary: str


def rewrite_iteratively(original_text: str, summary: str, depth=2):
    resummarizer = Resummarizer(original_text=original_text, summary=summary)
    for _ in range(depth):
        feedback = resummarizer.extract()
        resummarizer.summary = feedback.rewritten_summary
    return feedback.rewritten_summary


original_text = """
In the heart of a dense forest, a boy named Timmy pitched his first tent, fumbling with the poles and pegs.
His grandfather, a seasoned camper, guided him patiently, their bond strengthening with each knot tied.
As night fell, they sat by a crackling fire, roasting marshmallows and sharing tales of old adventures.
Timmy marveled at the star-studded sky, feeling a sense of wonder he'd never known.
By morning, the forest had transformed him, instilling a love for the wild that would last a lifetime.
"""

summarizer = Summarizer(original_text=original_text)
summary = summarizer.call().content
print(f"Summary: {summary}")
# > Summary: During a camping trip in a dense forest, Timmy, guided by his grandfather, experienced a transformative bonding moment and developed a lifelong love for the wilderness.
rewritten_summary = rewrite_iteratively(original_text, summary)
print(f"Rewritten Summary: {rewritten_summary}")
# > Rewritten Summary: During a camping trip in a dense forest, Timmy, guided by his seasoned camper grandfather, fumbled with the tent, bonded over a crackling fire and marshmallows, marveled at a star-studded sky, and discovered a profound, lifelong love for the wilderness.
