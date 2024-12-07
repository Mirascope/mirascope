# Quickstart

Mirascope supports various LLM providers, including [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Mistral](https://mistral.ai/), [Gemini](https://gemini.google.com), [Groq](https://groq.com/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Vertex AI](https://cloud.google.com/vertex-ai). For the purposes of this guide, we will be using OpenAI.

## Setup

Let's start by installing Mirascope and its dependencies:


```python
!pip install "mirascope[openai]"
```

This command installs Mirascope along with the necessary packages for the OpenAI integration.


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Basic LLM Call

The `call` decorator in Mirascope transforms Python functions into LLM API calls. This allows you to seamlessly integrate LLM interactions into your Python code.


```python
from mirascope.core import openai


@openai.call("gpt-4o-mini")
def get_capital(country: str) -> str:
    return f"What is the capital of {country}?"


response = get_capital("Japan")
print(response.content)
```

    The capital of Japan is Tokyo.


In this example:
1. We import the `openai` module from Mirascope, which provides the `call` decorator.
2. The `@openai.call("gpt-4o-mini")` decorator specifies which OpenAI model to use.
3. We return the content of a single user message in the function body.
4. When we call `get_capital("Japan")`, it templates the prompt, sends a request to the OpenAI API, and returns the response.
5. We print the `content` of the response, which contains the LLM's answer.

This approach allows you to use LLMs as if they were regular Python functions, making it easy to integrate AI capabilities into your applications. For more advanced usage, including controlling model parameters and handling errors, see our [documentation on Calls](../../../learn/calls).

## Streaming Responses

Streaming allows you to process LLM responses in real-time, which is particularly useful for long-form content generation or when you want to provide immediate feedback to users.


```python
@openai.call("gpt-4o-mini", stream=True)
def stream_city_info(city: str) -> str:
    return f"Provide a brief description of {city}."


for chunk, _ in stream_city_info("Tokyo"):
    print(chunk.content, end="", flush=True)
```

    Tokyo, the capital of Japan, is a vibrant metropolis known for its unique blend of tradition and modernity. As one of the world's most populous cities, it features a bustling urban landscape filled with skyscrapers, renowned shopping districts like Shibuya and Ginza, and cultural landmarks such as the historic Senso-ji Temple. Tokyo is also famous for its diverse culinary scene, ranging from street food to Michelin-starred restaurants. The city's efficient public transportation system makes it easy to explore its many neighborhoods, each offering distinct experiences, whether it’s the tranquil gardens of Ueno, the electronic town of Akihabara, or the fashion-forward streets of Harajuku. With its rich cultural heritage, cutting-edge technology, and constant innovation, Tokyo embodies the essence of contemporary urban life.

Here's what's happening in this streaming example:
1. We use the `stream=True` parameter in the `@openai.call` decorator to enable streaming.
2. The function returns an iterator that yields chunks of the response as they become available.
3. We iterate over the chunks, printing each one immediately.
4. The `end=""` and `flush=True` parameters in the print function ensure that the output is displayed in real-time without line breaks.

Streaming is beneficial for:
- Providing immediate feedback to users
- Processing very long responses efficiently
- Implementing typewriter-like effects in user interfaces

For more advanced streaming techniques, including error handling and processing streamed content, refer to our [documentation on Streams](../../../learn/streams).

## Response Models

Response models in Mirascope allow you to structure and validate the output from LLMs. This feature is particularly useful when you need to ensure that the LLM's response adheres to a specific format or contains certain fields.


```python
from pydantic import BaseModel


class Capital(BaseModel):
    city: str
    country: str


@openai.call("gpt-4o-mini", response_model=Capital)
def extract_capital(query: str) -> str:
    return f"{query}"


capital = extract_capital("The capital of France is Paris")
print(capital)
```

    city='Paris' country='France'


For more details on response models, including advanced validation techniques, check our [documentation on Response Models](../../../learn/response_models).

## Asynchronous Processing

Mirascope supports asynchronous processing, allowing for efficient parallel execution of multiple LLM calls. This is particularly useful when you need to make many LLM calls concurrently or when working with asynchronous web frameworks.


```python
import asyncio


@openai.call("gpt-4o-mini", response_model=Capital)
async def get_capital_async(country: str) -> str:
    return f"What is the capital of {country}?"


async def main():
    countries = ["France", "Japan", "Brazil"]
    tasks = [get_capital_async(country) for country in countries]
    capitals = await asyncio.gather(*tasks)
    for capital in capitals:
        print(f"The capital of {capital.country} is {capital.city}")


# await main() when running in a Jupyter notebook
await main()

# asyncio.run(main()) when running in a Python script
```

    The capital of France is Paris
    The capital of Japan is Tokyo
    The capital of Brazil is Brasília


This asynchronous example demonstrates:
1. An async version of our `get_capital` function, defined with `async def`.
2. Use of `asyncio.gather()` to run multiple async tasks concurrently.
3. Processing of results as they become available.

Asynchronous processing offers several advantages:
- Improved performance when making multiple LLM calls
- Better resource utilization
- Compatibility with async web frameworks like FastAPI or aiohttp

For more advanced asynchronous techniques, including error handling and async streaming, refer to our [documentation on Async](../../../learn/async).

## JSON Mode

JSON mode allows you to directly parse LLM outputs as JSON. This is particularly useful when you need structured data from your LLM calls.


```python
@openai.call("gpt-4o-mini", json_mode=True)
def city_info(city: str) -> str:
    return f"Provide information about {city} in JSON format"


response = city_info("Tokyo")
print(response.content)  # This will be a JSON-formatted string
```

    {
      "city": "Tokyo",
      "country": "Japan",
      "population": 13929286,
      "area_km2": 2191,
      "language": ["Japanese"],
      "currency": {
        "name": "Yen",
        "symbol": "¥"
      },
      "landmarks": [
        {
          "name": "Tokyo Tower",
          "type": "Observation Tower"
        },
        {
          "name": "Shibuya Crossing",
          "type": "Famous Intersection"
        },
        {
          "name": "Senso-ji Temple",
          "type": "Historic Site"
        },
        {
          "name": "Meiji Shrine",
          "type": "Shinto Shrine"
        }
      ],
      "transportation": {
        "rail": {
          "types": ["Subway", "Light Rail", "High-Speed Rail"],
          "notable_lines": ["Yamanote Line", "Chuo Line", "Tozai Line"]
        },
        "airport": ["Narita International Airport", "Haneda Airport"]
      },
      "cuisine": [
        "Sushi",
        "Ramen",
        "Tempura",
        "Yakitori"
      ],
      "climate": {
        "type": "Humid subtropical",
        "average_temperature": {
          "summer": "26°C",
          "winter": "5°C"
        },
        "average_precipitation_mm": 1650
      }
    }


JSON mode is beneficial for:
- Ensuring structured outputs from LLMs
- Easy integration with data processing pipelines
- Creating APIs that return JSON data

Note that not all providers have an explicit JSON mode. For those providers, we attempt to instruct the model to provide JSON; however, there is no guarantee that it will output only JSON (it may start with some text like "Here is the JSON: ..."). This is where Output Parsers can be useful.

It's also worth noting that you can combine `json_mode=True` with `response_model` to automatically parse the JSON output into a Pydantic model. This approach combines the benefits of JSON mode with the type safety and validation of response models. Here's an example:


```python
from pydantic import BaseModel


class CityInfo(BaseModel):
    name: str
    population: int
    country: str


@openai.call("gpt-4o-mini", json_mode=True, response_model=CityInfo)
def city_info(city: str) -> str:
    return f"Provide information about {city} in JSON format"


response = city_info("Tokyo")
print(
    f"Name: {response.name}, Population: {response.population}, Country: {response.country}"
)
```

    Name: Tokyo, Population: 13929286, Country: Japan


For more information on JSON mode and its limitations with different providers, refer to our [documentation on JSON Mode](../../../learn/json_mode).

## Output Parsers

Output parsers allow you to process LLM responses in custom formats. They are particularly useful when working with JSON outputs, especially for providers like Anthropic that don't have a strict JSON mode.


```python
!pip install "mirascope[anthropic]"
```


```python
import json

from mirascope.core import anthropic


def only_json(response: anthropic.AnthropicCallResponse) -> str:
    json_start = response.content.index("{")
    json_end = response.content.rfind("}")
    return response.content[json_start : json_end + 1]


@anthropic.call("claude-3-5-sonnet-20240620", json_mode=True, output_parser=only_json)
def json_extraction(text: str, fields: list[str]) -> str:
    return f"Extract {fields} from the following text: {text}"


json_response = json_extraction(
    text="The capital of France is Paris",
    fields=["capital", "country"],
)
print(json.loads(json_response))
```

    {'capital': 'Paris', 'country': 'France'}


In this example:
1. We define a custom `only_json` parser that extracts the JSON portion from the response.
2. We use both `json_mode=True` and the custom output parser to ensure we get clean JSON output.
3. The `json_extraction` function demonstrates how to combine JSON mode with a custom parser.

Output parsers are useful for:
- Extracting specific formats or data structures from LLM responses
- Cleaning and standardizing LLM outputs
- Implementing custom post-processing logic

For more information on output parsers and advanced usage scenarios, see our [documentation on Output Parsers](../../../learn/output_parsers).

## Next Steps

This concludes our Quickstart Guide to Mirascope. We've covered the main features of the library, including prompt templates, basic calls, streaming, response models, asynchronous processing, JSON mode, and output parsers. Each of these features can be combined and customized to create powerful, flexible AI applications.

If you like what you've seen so far, [give us a star](https://github.com/Mirascope/mirascope) and [join our community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA).

We recommend checking out our other getting started notebooks for more advanced usage:
- [Structured Outputs](../structured_outputs)
- [Dynamic Configuration & Chaining](../dynamic_configuration_and_chaining)
- [Tools & Agents](../tools_and_agents)

Check out our more comprehensive [Learn documentation](../../../learn) for more detailed information on Mirascope's features.
