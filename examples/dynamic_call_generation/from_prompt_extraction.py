"""Using Mirascope `from_prompt` to demonstrate a singular prompt with multiple providers.

This example has a base `PoemEvaluator` class that is used to evaluate a poem. Multiple
other evaluators are created from `PoemEvaluator` using `from_prompt`, and the results
of each evaluator are stored in results.
"""
import asyncio
import os
from typing import Literal

from google.generativeai import configure  # type: ignore
from pydantic import BaseModel, Field

from mirascope.anthropic import AnthropicCallParams, AnthropicExtractor
from mirascope.base import BaseCallParams, BaseExtractor
from mirascope.groq import GroqCallParams, GroqExtractor
from mirascope.openai import OpenAICall, OpenAICallParams, OpenAIExtractor

configure(api_key=os.getenv("GEMINI_API_KEY"))
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
os.environ["ANTHROPIC_API_KEY"] = "YOUR_ANTHROPIC_API_KEY"
os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY"


class PoemPrompt(OpenAICall):
    prompt_template = "Write a poem about {topic}"

    topic: str


judges: list[tuple[type[BaseExtractor], BaseCallParams]] = [
    (OpenAIExtractor, OpenAICallParams()),
    (AnthropicExtractor, AnthropicCallParams()),
    (GroqExtractor, GroqCallParams()),
]


class Evaluation(BaseModel):
    reasoning: str = Field(..., description="The reasoning behind the score.")
    score: Literal[0, 1, 2, 3, 4, 5] = Field(..., description="A score between 0 and 5")


class PoemEvaluator(OpenAIExtractor[Evaluation]):
    extract_schema: type[Evaluation] = Evaluation
    prompt_template = """
    Evaluate the poem about {topic} on a scale from 0 to 5.

    0 - Terrible
    1 - Bad
    2 - OK
    3 - Good
    4 - Great
    5 - Excellent

    Give a reasoning for the score
    
    {poem}
    """

    topic: str
    poem: str


topic = "memories"


async def evaluate_poem(topic: str) -> None:
    response = await PoemPrompt(topic=topic).call_async()
    content = response.content
    responses: list[Evaluation] = []
    for extractor_type, extractor_params in judges:
        extractor = extractor_type.from_prompt(PoemEvaluator, extractor_params)
        evaluation = await extractor(topic=topic, poem=content).extract_async()
        responses.append(evaluation)
    print(responses)


asyncio.run(evaluate_poem(topic))
