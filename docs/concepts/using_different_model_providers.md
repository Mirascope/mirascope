# Using different model providers

Testing out various providers is a powerful way to boost the performance of your calls. Mirascope makes it fast and simple to swap between various providers.

We currently support the following providers:

- OpenAI
- Anthropic
- Gemini
- Mistral (coming soon...)

This also means that we support any providers that use these APIs.

## Using providers that support the OpenAI API

If you want to use a provider that supports the OpenAI API, simply update the base_url.

This works for endpoints such as:

- [Ollama](https://ollama.com/)
- [Anyscale](https://www.anyscale.com/)
- [Together](https://www.together.ai/)
- [Groq](https://groq.com/)
- and more…

```python
import os

from mirascope.openai import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "OTHER_PROVIDER_API_KEY"


class RecipeRecommender(OpenAICall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    base_url = "BASE_URL"
    call_params = OpenAICallParams(model="...")
```

## Swapping from OpenAI to Gemini

The [generative-ai library](https://github.com/GoogleCloudPlatform/generative-ai?tab=readme-ov-file) and [openai-python library](https://github.com/openai/openai-python) are vastly different from each other, so swapping between them to attempt to gain better prompt responses is not worth the engineering effort and maintenance. 

This leads to people typically sticking with one provider even when providers release new features frequently. Take for example when Google announced [Gemini 1.5](https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/#gemini-15), it would be very useful to implement prompts with the new context window. Thankfully, Mirascope makes this swap trivial.

### Assuming you are starting with OpenAICall

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

1. First install Mirascope’s integration with gemini if you haven’t already.

```python
pip install mirascope[gemini]
```

1. Swap out OpenAI with Gemini:
    1. Replace `OpenAICall` and `OpenAICallParams` with `GeminiCall` and `GeminiCallParams` respectively 
    2. Configure your Gemini API Key
    3. Update `GeminiCallParams` with new model and other attributes

```python
from google.generativeai import configure
from mirasope.gemini import GeminiPrompt, GeminiCallParams

configure(api_key="YOUR_GEMINI_API_KEY")


class RecipeRecommender(GeminiCall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = GeminiCallParams(model="gemini-1.0-pro")


response = RecipeRecommender(ingredient="apples").call()
print(response.content)
```

That’s it for the basic example! Now you can evaluate the quality of your prompt with Gemini.

### Something a bit more advanced

What if you want to use a more complex message? The steps above are all the same except with one extra step.

Consider this OpenAI example:

```python
from mirascope import OpenAIPrompt, OpenAICallParams
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
from mirasope.gemini import GeminiPrompt, GeminiCallParams

configure(api_key="YOUR_GEMINI_API_KEY")


class Recipe(GeminiPrompt):
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

## Swapping to another provider

While the example above uses OpenAI to Gemini, the same applies to any provider that we support. If there’s a provider you would like us to support request the feature on our [GitHub Issues page](https://github.com/Mirascope/mirascope/issues) or [contribute](../CONTRIBUTING.md) a PR yourself.
