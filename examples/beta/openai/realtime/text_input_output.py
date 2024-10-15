import asyncio
from typing import Any

from mirascope.beta.openai import Context, Realtime, async_input

app = Realtime(
    "gpt-4o-realtime-preview-2024-10-01",
    modalities=["text"],
)


@app.receiver("text")
async def receive_text(response: str, context: dict[str, Any]) -> None:
    print(f"AI(text): {response}", flush=True)


@app.sender(wait_for_text_response=True)
async def send_message(context: Context) -> str:
    message = await async_input("Enter your message: ")
    return message


asyncio.run(app.run())
