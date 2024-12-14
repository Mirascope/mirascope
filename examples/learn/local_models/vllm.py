import asyncio

from mirascope.core import openai
from openai import AsyncOpenAI


# Follow the link to see what features of openai are supported
# https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
vllm_client = AsyncOpenAI(
    base_url = 'http://localhost:8000/v1', # your vLLM endpoint
    api_key='unused', # required by openai, but unused
)


@openai.call("llama3.2", client=vllm_client)
async def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


async def main():
    recommendation = await recommend_book("fantasy")
    print(recommendation)
    # Output: Here are some popular and highly-recommended fantasy books...

asyncio.run(main())

