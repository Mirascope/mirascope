# Streaming generated content

Streaming generated content is similar to [Generating Content](generating_content.md) so check that out if you haven’t already.

## OpenAIPrompt

We will be using the same `OpenAICall` in [Generating Content](generating_content.md). Feel free to swap it out with a different provider.

### Streaming

You can use the [`stream`](../api/openai/calls.md#mirascope.openai.calls.OpenAICall.stream) method to stream a response. All this is doing is setting `stream=True` and providing the [`OpenAICallResponseChunk`](../api/openai/types.md#mirascope.openai.types.OpenAICallResponseChunk) convenience wrappers around the response chunks.

```python
import os
from mirascope import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class RecipeRecommender(OpenAIPrompt):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


stream = RecipeRecommender(ingredient="apples").stream()

for chunk in stream:
	print(chunk.content, end="")
```

### Async

If you want concurrency, you can use the `stream_async` function instead.

```python
import os

from mirascope import OpenAIPrompt, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class RecipeRecommender(OpenAIPrompt):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


async def stream_recipe_recommendation():
    """Asynchronously streams the response for a call to the model using `OpenAICall`."""
	stream = RecipeRecommender(ingredient="apples").async_stream()
    async for chunk in astream:
        print(chunk.content, end="")

asyncio.run(stream_recipe_recommendation())
```

### OpenAICallResponseChunk

The `stream` method returns an [`OpenAICallResponseChunk`](../api/openai/types.md#mirascope.openai.types.OpenAICallResponseChunk) instance, which is a convenience wrapper around the [`ChatCompletionChunk`](https://platform.openai.com/docs/api-reference/chat/streaming) class in `openai`

```python
from mirascope.openai.types import OpenAIChatCompletionChunk

chunk = OpenAICallResponseChunk(...)

chunk.content  # original.choices[0].delta.content
chunk.delta    # original.choices[0].delta
chunk.choice   # original.choices[0]
chunk.choices  # original.choices
chunk.chunk    # ChatCompletionChunk(...)
```
