"""Basic example using an @openai_call to make an async call."""
import asyncio
import os

from mirascope.core.openai import openai_call

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai_call(model="gpt-4o")
async def recommend_book(genre: str):
    """Recommend a {genre} book."""


async def run():
    results = await recommend_book(genre="fiction")
    print(results.content)
    # > Certainly! If you're looking for a compelling fiction book, I highly recommend
    #   "The Night Circus" by Erin Morgenstern. ...
    print(results.cost)
    print(results.usage)
    # > CompletionUsage(completion_tokens=116, prompt_tokens=12, total_tokens=128)
    print(results.message_param)
    # > {
    #       "content": 'Certainly! If you haven\'t read it yet, I highly recommend "The Night Circus" by Erin Morgenstern. ...',
    #       "role": "assistant",
    #       "tool_calls": None,
    #   }
    print(results.user_message_param)
    # > {"content": "Recommend a fiction book.", "role": "user"}


asyncio.run(run())
