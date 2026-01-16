import asyncio

from mirascope import llm


@llm.tool
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city."""
    await asyncio.sleep(0.1)  # Simulate async API call
    return f"72°F and sunny in {city}"


@llm.call("openai/gpt-5-mini", tools=[fetch_weather])
async def weather_assistant(query: str):
    return query


async def main():
    response = await weather_assistant("What's the weather in Tokyo?")

    while response.tool_calls:
        tool_outputs = await response.execute_tools()
        response = await response.resume(tool_outputs)

    print(response.pretty())


asyncio.run(main())
