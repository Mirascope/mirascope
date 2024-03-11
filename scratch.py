import os

from mirascope.mistral.prompt import MistralPrompt
from mirascope.mistral.types import MistralCallParams

os.getenv("MISTRAL_API_KEY")


def get_weather(city: str) -> int:
    """Gives the weather of a city.

    Args:
        city: the city to get the weather from.

    Returns:
        The temperature of given city.
    """
    return 65


class example(MistralPrompt):
    """What is the temperature in Seoul?"""

    call_params: MistralCallParams(tools=[get_weather])


prompt = example()
# response = prompt.create(tools=[get_weather])
response = prompt.create()
print(response, response.model_dump())
