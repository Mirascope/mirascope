from mirascope import llm


@llm.call("anthropic/claude-sonnet-4-5", tools=[llm.WebSearchTool()])
def weather_assistant(query: str):
    return query


response = weather_assistant("What's the current weather in San Francisco?")
print(response.text())
# Today features intervals of clouds and sunshine with a couple of showers, with a high of 62°F
# Partly cloudy skies this morning will give way to occasional showers during the afternoon, with a high of 61°F and a 40% chance of rain

# Tonight, expect light rain transitioning to a few showers by morning, with a low of 51°F and a 60% chance of rain
# The air quality is poor and unhealthy for sensitive groups
