from google.generativeai import configure  # type: ignore

from mirascope.gemini import GeminiCallParams, GeminiPrompt, GeminiTool

configure(api_key="YOUR_GEMINI_API_KEY")


class CurrentWeather(GeminiTool):
    """A tool for getting the current weather in a location."""

    location: str


class WeatherPrompt(GeminiPrompt):
    """What is the current weather in Tokyo?"""

    call_params = GeminiCallParams(
        model="gemini-pro",
        tools=[CurrentWeather],
    )


prompt = WeatherPrompt()
current_weather = prompt.create().tool
print(current_weather.location)  # type: ignore
