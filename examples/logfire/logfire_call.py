import os

from dotenv import find_dotenv, load_dotenv
from google.generativeai import configure

from mirascope.anthropic import AnthropicCall
from mirascope.gemini import GeminiCall
from mirascope.logfire import with_logfire

# logfire.configure()

load_dotenv(find_dotenv())

configure(api_key=os.getenv("GEMINI_API_KEY"))


@with_logfire
class BookRecommender(GeminiCall):
    prompt_template = "Please recommend some {genre} books"

    genre: str


recommender = BookRecommender(genre="fantasy")
print(recommender.call().content)
# async def foo():
#     @with_logfire
#     class BookRecommender(AnthropicCall):
#         prompt_template = "Please recommend some {genre} books"

#         genre: str

#     recommender = BookRecommender(genre="fantasy")
#     stream = recommender.stream_async()
#     async for chunk in stream:
#         print(chunk.content, end="", flush=True)


# asyncio.run(foo())
# foo()
