import asyncio
from typing import Any, Callable

from mirascope.beta.openai import Context, Realtime, async_input

from mirascope.beta.openai import OpenAIRealtimeTool

app = Realtime(
    "gpt-4o-realtime-preview-2024-10-01",
    modalities=["text"],
)


def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"


@app.sender(wait_for_text_response=True)
async def send_message(context: Context) -> tuple[str, list[Callable]]:
    genre = await async_input("Enter a genre: ")
    return f"Recommend a {genre} book. please use the tool `format_book`.", [
        format_book
    ]


@app.receiver("text")
async def receive_text(response: str, context: dict[str, Any]) -> None:
    print(f"AI(text): {response}", flush=True)


@app.function_call(format_book)
async def recommend_book(tool: OpenAIRealtimeTool, context: Context) -> str:
    result = tool.call()
    print(result)
    return result


asyncio.run(app.run())
