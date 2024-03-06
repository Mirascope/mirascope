from google.generativeai import configure  # type: ignore

from mirascope.gemini import GeminiCallParams, GeminiPrompt

configure(api_key="YOUR_GEMINI_API_KEY")


def get_current_weather(location: str) -> int:
    """Get the current weather in a given location."""
    return 65


class WeatherPrompt(GeminiPrompt):
    """What is the current weather in Tokyo?"""

    call_params = GeminiCallParams(
        model="gemini-pro",
        tools=[get_current_weather],
    )


tool = WeatherPrompt().create().tool
print(tool.fn(tool.model_dump()))  # type: ignore
