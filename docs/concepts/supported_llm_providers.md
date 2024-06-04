# Supported LLM Providers

With new models dropping every week, it's important to be able to quickly test out different models. This can be an easy and powerful way to boost the performance of your application. Mirascope provides a unified interface that makes it fast and simple to swap between various providers.

We currently support the following providers:

- [OpenAI](https://platform.openai.com/docs/quickstart?context=python)
- [Anthropic](https://docs.anthropic.com/claude/docs/quickstart-guide)
- [Mistral](https://docs.mistral.ai/)
- [Cohere](https://docs.cohere.com/docs/the-cohere-platform)
- [Groq](https://console.groq.com/docs/quickstart)
- [Gemini](https://ai.google.dev/tutorials/get_started_web)

This also means that we support any providers that use these APIs.

!!! note

    If there’s a provider you would like us to support that we don't yet support, please request the feature on our [GitHub Issues page](https://github.com/Mirascope/mirascope/issues) or [contribute](../CONTRIBUTING.md) a PR yourself.

## Examples

For the majority of cases, switching providers when using Mirascope requires just 2-3 changes:

1. Change the `mirascope.{provider}` import to the new provider
2. Update your class to use the new provider
3. Update any specific call params such as `model`

### Calls

=== "OpenAI"

    ```python hl_lines="1 4 9"
    from mirascope.openai import OpenAICall, OpenAICallParams


    class BookRecommender(OpenAICall):
        prompt_template = "Please recommend a {genre} book."

        genre: str

        call_params = OpenAICallParams(model="gpt-4-turbo")


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    # > The Name of the Wind by Patrick Rothfuss
    ```

=== "Anthropic"

    ```python hl_lines="1 4 9"
    from mirascope.anthropic import AnthropicCall, AnthropicCallParams


    class BookRecommender(AnthropicCall):
        prompt_template = "Please recommend a {genre} book."

        genre: str

        call_params = AnthropicCallParams(model="claude-3-haiku-20240307")


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    # > The Name of the Wind by Patrick Rothfuss
    ```

=== "Mistral"

    ```python hl_lines="1 4 9"
    from mirascope.mistral import MistralCall, MistralCallParams


    class BookRecommender(MistralCall):
        prompt_template = "Please recommend a {genre} book."

        genre: str

        call_params = MistralCallParams(model="mistral-large-latest")


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    # > The Name of the Wind by Patrick Rothfuss
    ```

=== "Cohere"

    ```python hl_lines="1 4 9"
    from mirascope.cohere import CohereCall, CohereCallParams


    class BookRecommender(CohereCall):
        prompt_template = "Please recommend a {genre} book."

        genre: str

        call_params = CohereCallParams(model="command-r-plus")


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    # > The Name of the Wind by Patrick Rothfuss
    ```

=== "Groq"

    ```python hl_lines="1 4 9"
    from mirascope.groq import GroqCall, GroqCallParams


    class BookRecommender(GroqCall):
        prompt_template = "Please recommend a {genre} book."

        genre: str

        call_params = GroqCallParams(model="mixtral-8x7b-32768")


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    # > The Name of the Wind by Patrick Rothfuss
    ```

=== "Gemini"

    ```python hl_lines="1 4 9"
    from mirascope.gemini import GeminiCall, GeminiCallParams


    class BookRecommender(GeminiCall):
        prompt_template = "Please recommend a {genre} book."

        genre: str

        call_params = GeminiCallParams(model="gemini-1.0-pro-latest")


    response = BookRecommender(genre="fantasy").call()
    print(response.content)
    # > The Name of the Wind by Patrick Rothfuss
    ```

### Extractors

=== "OpenAI"

    ```python hl_lines="5 14"
    from typing import Literal, Type

    from pydantic import BaseModel

    from mirascope.openai import OpenAIExtractor


    class TaskDetails(BaseModel):
        description: str
        due_date: str
        priority: Literal["low", "normal", "high"]


    class TaskExtractor(OpenAIExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails
        prompt_template = """
        Extract the task details from the following task:
        {task}
        """

        task: str


    task = "Submit quarterly report by next Friday. Task is high priority."
    task_details = TaskExtractor(task=task).extract()
    assert isinstance(task_details, TaskDetails)
    print(task_details)
    # > description='Submit quarterly report' due_date='next Friday' priority='high'
    ```

=== "Anthropic"

    ```python hl_lines="5 14"
    from typing import Literal, Type

    from pydantic import BaseModel

    from mirascope.anthropic import AnthropicExtractor


    class TaskDetails(BaseModel):
        description: str
        due_date: str
        priority: Literal["low", "normal", "high"]


    class TaskExtractor(AnthropicExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails
        prompt_template = """
        Extract the task details from the following task:
        {task}
        """

        task: str


    task = "Submit quarterly report by next Friday. Task is high priority."
    task_details = TaskExtractor(task=task).extract()
    assert isinstance(task_details, TaskDetails)
    print(task_details)
    # > description='Submit quarterly report' due_date='next Friday' priority='high'
    ```

=== "Mistral"

    ```python hl_lines="5 14"
    from typing import Literal, Type

    from pydantic import BaseModel

    from mirascope.mistral import MistralExtractor


    class TaskDetails(BaseModel):
        description: str
        due_date: str
        priority: Literal["low", "normal", "high"]


    class TaskExtractor(MistralExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails
        prompt_template = """
        Extract the task details from the following task:
        {task}
        """

        task: str


    task = "Submit quarterly report by next Friday. Task is high priority."
    task_details = TaskExtractor(task=task).extract()
    assert isinstance(task_details, TaskDetails)
    print(task_details)
    # > description='Submit quarterly report' due_date='next Friday' priority='high'
    ```

=== "Cohere"

    ```python hl_lines="5 14"
    from typing import Literal, Type

    from pydantic import BaseModel

    from mirascope.cohere import CohereExtractor


    class TaskDetails(BaseModel):
        description: str
        due_date: str
        priority: Literal["low", "normal", "high"]


    class TaskExtractor(CohereExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails
        prompt_template = """
        Extract the task details from the following task:
        {task}
        """

        task: str


    task = "Submit quarterly report by next Friday. Task is high priority."
    task_details = TaskExtractor(task=task).extract()
    assert isinstance(task_details, TaskDetails)
    print(task_details)
    # > description='Submit quarterly report' due_date='next Friday' priority='high'
    ```

=== "Groq"

    ```python hl_lines="5 14"
    from typing import Literal, Type

    from pydantic import BaseModel

    from mirascope.groq import GroqExtractor


    class TaskDetails(BaseModel):
        description: str
        due_date: str
        priority: Literal["low", "normal", "high"]


    class TaskExtractor(GroqExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails
        prompt_template = """
        Extract the task details from the following task:
        {task}
        """

        task: str


    task = "Submit quarterly report by next Friday. Task is high priority."
    task_details = TaskExtractor(task=task).extract()
    assert isinstance(task_details, TaskDetails)
    print(task_details)
    # > description='Submit quarterly report' due_date='next Friday' priority='high'
    ```

=== "Gemini"

    ```python hl_lines="5 14"
    from typing import Literal, Type

    from pydantic import BaseModel

    from mirascope.gemini import GeminiExtractor


    class TaskDetails(BaseModel):
        description: str
        due_date: str
        priority: Literal["low", "normal", "high"]


    class TaskExtractor(GeminiExtractor[TaskDetails]):
        extract_schema: Type[TaskDetails] = TaskDetails
        prompt_template = """
        Extract the task details from the following task:
        {task}
        """

        task: str


    task = "Submit quarterly report by next Friday. Task is high priority."
    task_details = TaskExtractor(task=task).extract()
    assert isinstance(task_details, TaskDetails)
    print(task_details)
    # > description='Submit quarterly report' due_date='next Friday' priority='high'
    ```

!!! note

    If you are accessing features that are specific to a particular provider, switching can require a little more work. For example, Gemini has a different structure for messages from other providers, so if you're writing your own `messages` function, you'll need to make sure you update to conform to the new provider's messages structure. See the [example section](./supported_llm_providers.md#more-detailed-walkthrough-of-swapping-providers-openai-gemini) below for more details.

## Settings `base_url` and `api_key`

If you want to use a proxy, you can easily set the `base_url` class variable for any call. You can do the same to set the `api_key`. This is key for using providers such as [Ollama](https://ollama.com/), [Anyscale](https://www.anyscale.com/), [Together](https://www.together.ai/), and others that support the `OpenAI` API through a proxy.

Here's an example using Ollama:

```python
import os

from mirascope.openai import OpenAICall, OpenAICallParams


class RecipeRecommender(OpenAICall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    api_key = "ollama"
    base_url = "http://localhost:11434/v1"
    call_params = OpenAICallParams(model="mistral")
```

## Using models hosted on major cloud providers

Some model providers have their models hosted on major cloud providers such as AWS Bedrock and Microsoft Azure. You can use provided client wrappers to access these models by providing the proper configuration:

=== "Anthropic (AWS Bedrock)"

    ```python
    import os

    from mirascope.anthropic import (
        AnthropicCall,
        AnthropicCallParams,
        bedrock_client_wrapper,
    )
    from mirascope.base import BaseConfig


    class BookRecommender(AnthropicCall):
        prompt_template = "Please recommend a fantasy book."

        call_params = AnthropicCallParams(model="anthropic.claude-3-haiku-20240307-v1:0")
        configuration = BaseConfig(
            client_wrappers=[
                bedrock_client_wrapper(
                    aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_region="us-west-2",
                )
            ]
        )


    recommender = BookRecommender()
    response = recommender.call()
    print(response.content)
    ```

=== "OpenAI (Microsoft Azure)"

    ```python
    import os

    from mirascope.base import BaseConfig
    from mirascope.openai import (
        OpenAICall,
        OpenAICallParams,
        azure_client_wrapper,
    )


    class BookRecommender(OpenAICall):
        prompt_template = "Please recommend a fantasy book."

        call_params = OpenAICallParams(model="NEEDS MODEL NAME ONCE FIGURED OUT")
        configuration = BaseConfig(
            client_wrappers=[
                azure_client_wrapper(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version="2024-02-01",
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                )
            ]
        )


    recommender = BookRecommender()
    response = recommender.call()
    print(response.content)
    ```

## More detailed walkthrough of swapping providers (OpenAI -> Gemini)

The [generative-ai library](https://github.com/GoogleCloudPlatform/generative-ai?tab=readme-ov-file) and [openai-python library](https://github.com/openai/openai-python) are vastly different from each other, so swapping between them to attempt to gain better prompt responses is not worth the engineering effort and maintenance. 

This leads to people typically sticking with one provider even when providers release new features frequently. Take for example when Google announced [Gemini 1.5](https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/#gemini-15), it would be very useful to implement prompts with the new context window. Thankfully, Mirascope makes this swap trivial.

The following examples are using `OpenAI` and `Gemini` so make sure Gemini is installed if you intend to follow along. Of course, the same concepts apply to all providers, so feel free to substitute `Gemini` with any provider:

```python
pip install mirascope[gemini]
```

### The simplest case

If you do not have provider-specific syntax (which we will go over later), you can take advantage of the `from_prompt` classmethod to do the heavy lifting for you.

```python hl_lines="14"
from google.generativeai import configure
from mirascope.gemini import GeminiCall, GeminiCallParams

configure(api_key="YOUR_GEMINI_API_KEY")

class RecipeRecommender(OpenAICall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = OpenAICallParams(model="...")


recipe_recommender = GeminiCall.from_prompt(RecipeRecommender, GeminiCallParams(model="gemini-1.0-pro"))
response = recipe_recommender(ingredient="apples").call()
print(response.content)
```

With just 1 line and some imports you can immediately test out other providers. You can also swap the provider class manually.

### The manual case

Assuming you are starting with OpenAICall:

```python
import os
from mirascope import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class RecipeRecommender(OpenAICall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = OpenAICallParams(model="...")


response = RecipeRecommender(ingredient="apples").call()
print(response.content)
```

Swap out OpenAI with Gemini:
    1. Replace `OpenAICall` and `OpenAICallParams` with `GeminiCall` and `GeminiCallParams` respectively 
    2. Configure your Gemini API Key
    3. Update `GeminiCallParams` with new model and other attributes

```python
from google.generativeai import configure
from mirasope.gemini import GeminiCall, GeminiCallParams

configure(api_key="YOUR_GEMINI_API_KEY")


class RecipeRecommender(GeminiCall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = GeminiCallParams(model="gemini-1.0-pro")


response = RecipeRecommender(ingredient="apples").call()
print(response.content)
```

That’s it for the manual example! Now you can evaluate the quality of your prompt with Gemini.

### Something a bit more advanced

What if you want to use a more complex message? The steps above are all the same except with one extra step.

Consider this OpenAI example:

```python
from mirascope import OpenAICall, OpenAICallParams
from openai.types.chat import ChatCompletionMessageParam


class Recipe(OpenAICall):
    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")
    
    @property
    def messages(self) -> list[ChatCompletionMessageParam]:
        return [
            {"role": "system", "content": "You are the world's greatest chef."},
            {"role": "user", "content": f"Can you recommend some recipes that use {self.ingredient} as an ingredient?"},
        ]
```

The Gemini example will look like this:

```python
from google.generativeai import configure
from google.generativeai.types import ContentsType
from mirasope.gemini import GeminiCall, GeminiCallParams

configure(api_key="YOUR_GEMINI_API_KEY")


class Recipe(GeminiCall):
    """A normal docstring"""
    
    ingredient: str
    
    call_params = GeminiCallParams(model="gemini-1.0-pro")
    
    @property
    def messages(self) -> ContentsType:
        return [
            {"role": "user", "parts": ["You are the world's greatest chef."]},
            {"role": "model", "parts": ["I am the world's greatest chef."]},
            {"role": "user", "parts": [f"Can you recommend some recipes that use {self.ingredient} as an ingredient?"]},
        ]
```

Update the return type from `list[ChatCompletionMessageParam]` to `ContentsType` for the `messages` method. Gemini doesn’t have a `system` role, so instead we need to simulate OpenAI’s `system` message using a `user` → `model` pair. Refer to the providers documentation on how to format their messages array.
