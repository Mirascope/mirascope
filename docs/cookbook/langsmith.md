# Integrating LangSmith with Mirascope

This recipe will walk you through how to use LangSmith’s tracing functionality with Mirascope.

## Before we get started

You will need a [LangSmith account](https://docs.smith.langchain.com/setup) and API key. Follow their docs on how to setup LangSmith. You will also need to have mirascope installed! Check out [Getting Started](https://docs.mirascope.io/latest/) if you have not installed mirascope yet. Finally, this example uses OpenAI so you will also need an [OpenAI API Key](https://platform.openai.com/docs/quickstart?context=python).

## Quick Refresher on Mirascope LLM Convenience Wrappers

Mirascope LLM Convenience Wrappers will simply passthrough any param you give it. This means that Mirascope will have any support that LangSmith has with OpenAI. Check out [Mirascope LLM Convenience Wrappers](https://docs.mirascope.io/latest/concepts/llm_convenience_wrappers/) for more details.

What this means is that Mirascope can take advantage of LangSmith’s `wrappers` function around OpenAI.

```python
from openai import OpenAI
from langsmith import wrappers

client = wrappers.wrap_openai(OpenAI())
```

with Mirascope it looks like this:

```python
from mirascope import OpenAIChat
from langsmith import wrappers

chat = OpenAIChat(client_wrapper=wrappers.wrap_openai)
```

…and now you have all of LangSmith’s integration with OpenAI with the power of Mirascope Prompts.

## Logging a LangSmith trace using Mirascope

### Setup your environment

Create a `.env` file with your secrets:

```python
LANGCHAIN_API_KEY=ls__...

OPENAI_API_KEY=...
```

We recommend leveraging [Pydantic Settings](https://github.com/pydantic/pydantic-settings) when getting your secrets. Create a `[config.py](http://config.py)` file:

```python
"""Global variables for LangSmith."""
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str = ""
    langchain_tracing_v2: Literal["true"] = "true"
    langchain_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")

```

Note that we keep non-secret settings inside `[config.py](http://config.py)` such as `LANGCHAIN_TRACING_V2`.

### Create prompt and chat

Now that the environment is setup, we will create `book_recommendation.py`

```python
import os

from langsmith import wrappers
from config import Settings

from mirascope import OpenAICallParams, OpenAIChat, Prompt

settings = Settings()

os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["OPENAI_API_KEY"] = settings.openai_api_key

class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str

    call_params = OpenAICallParams(
        model="gpt-3.5-turbo", temperature=0.1,
    )

prompt = BookRecommendationPrompt(topic="how to bake a cake")
chat = OpenAIChat(client_wrapper=wrappers.wrap_openai)
completion = chat.create(prompt)
print(completion)
```

### View your Trace

Login to [LangSmith](https://smith.langchain.com/) and view your results

![langsmith](https://github.com/Mirascope/mirascope/assets/15950811/6ac51f61-6c81-4c35-abc0-63a84e8b5bbd)

## Extract

Yes, this also works for extract and stream. Here is a simple extract example to demonstrate this.

```python
import os

from langsmith import wrappers
from langsmith_config import Settings
from pydantic import BaseModel

from mirascope import OpenAIChat

settings = Settings()

os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["OPENAI_API_KEY"] = settings.openai_api_key

class BookInfo(BaseModel):
    """A model for book info."""

    title: str
    author: str

chat = OpenAIChat(client_wrapper=wrappers.wrap_openai)
chat.extract(
    BookInfo,
    "The Name of the Wind is by Patrick Rothfuss.",
    retries=5,
)
```

## Adding Metadata to LangSmith

```python
completion = chat.create(
    prompt,
    langsmith_extra={"metadata": {"hello": "world"}}
)
```

## LangChain-specific

There may be some integrations of LangSmith specific to LangChain. In situations like this, we recommend you use Mirascope to replace LangChain prompts. This will enable you to receive all the benefits from LangChain-specific integrations with LangSmith while also benefitting from Prompt validation and type hints.

Check out our [basic examples](https://github.com/Mirascope/mirascope/tree/main/examples/langchain) of using Mirascope with LangChain.

## Prompt Engineering Should Not be Complex

By adding a few lines of code, you gain access to LangSmith’s wide array of development, monitoring, and testing. While this cookbook focuses on LangSmith, one benefit of using Mirascope is that any tool that integrates with OpenAI will automatically integrate with Mirascope.
