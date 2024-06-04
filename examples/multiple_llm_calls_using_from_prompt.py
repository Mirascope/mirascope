"""Using Mirascope `from_prompt` to demonstrate a singular prompt with multiple providers.

The example uses a base OpenAICall to generate a poem class. The poem prompt is then
copied to other providers. The poem is then evaluated by the judges which 
also uses `from_prompt` to create a new extractor.
"""
import asyncio
import os
from typing import Literal

from google.generativeai import configure  # type: ignore
from pydantic import BaseModel, Field

from mirascope.anthropic.calls import AnthropicCall
from mirascope.anthropic.extractors import AnthropicExtractor
from mirascope.anthropic.types import AnthropicCallParams
from mirascope.base.calls import BaseCall
from mirascope.base.extractors import BaseExtractor
from mirascope.base.types import BaseCallParams
from mirascope.gemini import GeminiCall, GeminiCallParams
from mirascope.groq import GroqCall, GroqCallParams
from mirascope.groq.extractors import GroqExtractor
from mirascope.openai import OpenAIExtractor
from mirascope.openai.calls import OpenAICall
from mirascope.openai.types import OpenAICallParams

configure(api_key="YOUR_GEMINI_API_KEY")
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
os.environ["ANTHROPIC_API_KEY"] = "YOUR_ANTHROPIC_API_KEY"
os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY"


class PoemPrompt(OpenAICall):
    prompt_template = "Write a poem about {topic}"

    topic: str


contestants: list[tuple[type[BaseCall], BaseCallParams]] = [
    (GeminiCall, GeminiCallParams(model="gemini-1.0-pro")),
    (OpenAICall, OpenAICallParams(model="gpt-4o-2024-05-13")),
    (AnthropicCall, AnthropicCallParams(model="claude-3-opus-20240229")),
    (GroqCall, GroqCallParams(model="mixtral-8x7b-32768")),
]

judges: list[tuple[type[BaseExtractor], BaseCallParams]] = [
    (OpenAIExtractor, OpenAICallParams()),
    (AnthropicExtractor, AnthropicCallParams()),
    (GroqExtractor, GroqCallParams()),
]


class Evaluation(BaseModel):
    poem: str = Field(..., description="The poem to evaluate.")
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
    winner: tuple[str, str, int, list[str]] = ("", "", 0, [])
    for call_type, call_params in contestants:
        poem = call_type.from_prompt(PoemPrompt, call_params)
        response = await poem(topic=topic).call_async()
        content = response.content
        scores = 0
        reasoning: list[str] = []
        for extractor_type, extractor_params in judges:
            extractor = extractor_type.from_prompt(PoemEvaluator, extractor_params)
            evaluation = await extractor(topic=topic, poem=content).extract_async()
            scores += evaluation.score
            reasoning.append(evaluation.reasoning)
            if evaluation.score > winner[2]:
                winner = (extractor_params.model, content, evaluation.score, reasoning)

    print(f"The winner is {winner[0]} with a score of {winner[2]}")
    print("Poem:", winner[1])
    print("Reasoning:", winner[3])


asyncio.run(evaluate_poem(topic))
