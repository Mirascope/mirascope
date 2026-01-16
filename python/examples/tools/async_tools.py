import asyncio

from mirascope import llm


@llm.tool
async def fetch_user_data(user_id: int) -> dict[str, str | int]:
    """Fetch user data from the database."""
    await asyncio.sleep(0.1)  # Simulate async I/O
    return {"id": user_id, "name": "Alice", "email": "alice@example.com"}


@llm.call("openai/gpt-4o", tools=[fetch_user_data])
async def user_assistant(query: str) -> str:
    return query


async def main():
    response = await user_assistant("Get info for user 123")

    if response.tool_calls:
        tool_outputs = await response.execute_tools()
        response = await response.resume(tool_outputs)

    print(response.pretty())


asyncio.run(main())
