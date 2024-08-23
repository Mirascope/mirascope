from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template

text = ""
with open("wikipedia-python.txt") as file:
    text = file.read()


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Summarize the following text:
    {text}
    """
)
def simple_summarize_text(text: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Summarize the following text by first creating an outline with a nested structure,
    listing all major topics in the text with subpoints for each of the major points.
    The number of subpoints for each topic should correspond to the length and
    importance of the major point within the text. Then create the actual summary using
    the outline.
    {text}
    """
)
def summarize_text_with_outline(text: str): ...


class SegmentedSummary(BaseModel):
    outline: str = Field(
        ...,
        description="A high level outline of major sections by topic in the text",
    )
    section_summaries: list[str] = Field(
        ..., description="A list of detailed summaries for each section in the outline"
    )


@openai.call(model="gpt-4o", response_model=SegmentedSummary)
@prompt_template(
    """
    Extract a high level outline and summary for each section of the following text:
    {text}
    """
)
def summarize_by_section(text): ...


@openai.call(model="gpt-4o")
@prompt_template(
    """
    The following contains a high level outline of a text along with summaries of a
    text that has been segmented by topic. Create a composite, larger summary by putting
    together the summaries according to the outline.
    Outline:
    {outline}

    Summaries:
    {summaries}
    """
)
def summarize_text_chaining(text: str) -> openai.OpenAIDynamicConfig:
    segmented_summary = summarize_by_section(text)
    return {
        "computed_fields": {
            "outline": segmented_summary.outline,
            "summaries": segmented_summary.section_summaries,
        }
    }
