# Generating content

Now that you have your prompt, you can combine it with a model call to generate content. Mirascope provides high-level wrappers around common providers so you can focus on prompt engineering instead of learning the interface for providers. Our high-level wrappers are not required to use our prompts but simply provide convenience if you wish to use it.

!!! note

    This doc uses OpenAI. See [supported LLM providers](./supported_llm_providers.md) for how to generate content with other model providers like Anthropic, Mistral, Cohere and more.

## OpenAICall

[`OpenAICall`](../api/openai/calls.md#mirascope.openai.calls.OpenAICall) extends [`BasePrompt`](../api/base/prompts.md#mirascope.base.prompts.BasePrompt) and [`BaseCall`](../api/base/calls.md#mirascope.base.calls.BaseCall) to support interacting with the OpenAI API.

### Call

You can initialize an [`OpenAICall`](../api/openai/calls.md#mirascope.openai.calls.OpenAICall) instance and call the [`call`](../api/openai/calls.md#mirascope.openai.calls.OpenAICall.call) method to generate an [`OpenAICallResponse`](../api/openai/types.md#mirascope.openai.types.OpenAICallResponse):

```python
import os

from mirascope import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class RecipeRecommender(OpenAICall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


response = RecipeRecommender(ingredient="apples").call()
print(response.content)  # prints the string content of the call
```

The `call_params` of the OpenAI client is tied to the call (and thereby the prompt).

### Async

If you want concurrency, you can use the `async` function instead.

```python
import asyncio
import os

from mirascope import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class RecipeRecommender(OpenAICall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


async def recommend_recipes():
    """Asynchronously calls the model using `OpenAICall` to generate a recipe."""
    return await RecipeRecommender(ingredient="apples").call_async()


print(asyncio.run(recommend_recipes())) 
```

### CallResponse

The `call` method returns an [`OpenAICallResponse`](../api/openai/types.md#mirascope.openai.types.OpenAICallResponse) class instance, which is a simple wrapper around the [`ChatCompletion`](https://platform.openai.com/docs/api-reference/chat/object) class in `openai` that extends [`BaseCallResponse`](../api/base/types.md#mirascope.base.types.BaseCallResponse). In fact, you can access everything from the original response as desired. The primary purpose of the class is to provide convenience and typing for a better developer experience.

```python
from mirascope.openai.types import OpenAICallResponse

response = OpenAICallResponse(...)

response.content     # original.choices[0].message.content
response.tool_calls  # original.choices[0].message.tool_calls
response.message     # original.choices[0].message
response.choice      # original.choices[0]
response.choices     # original.choices
response.response    # ChatCompletion(...)
response.cost        # Mirascope only: Takes the usage and model and calculates cost in dollars
```
