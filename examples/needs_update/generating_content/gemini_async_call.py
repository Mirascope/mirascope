"""Basic example using an @gemini.call_async to make an async call."""

import asyncio

from google.generativeai import configure

from mirascope.core import gemini

configure(api_key="YOUR_GEMINI_API_KEY")


@gemini.call_async(model="gemini-1.5-flash-latest")
async def recommend_book(genre: str):
    """Recommend a {genre} book."""


async def run():
    results = await recommend_book(genre="fiction")
    print(results.content)
    # > Certainly! If you're looking for a compelling fiction book, I highly recommend
    #   "The Night Circus" by Erin Morgenstern. ...
    print(results.cost)
    # > None
    print(results.usage)
    # > None
    print(results.message_param)
    # > {
    #       "parts": [text: 'Certainly! If you haven\'t read it yet, I highly recommend "The Night Circus" by Erin Morgenstern. ...'],
    #       "role": "model",
    #       "tool_calls": None,
    #   }
    print(results.user_message_param)
    # {"parts": ["Recommend a fiction book."], "role": "user"}


asyncio.run(run())
