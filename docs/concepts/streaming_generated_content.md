# Streaming generated content

Streaming generated content is similar to [Generating Content](generating_content.md) so check that out if you haven’t already.

## OpenAIPrompt

We will be using the same `OpenAIPrompt` in [Generating Content](generating_content.md). Feel free to swap it out with a different provider.

### Streaming

You can use the [`stream`](../api/openai/prompt.md#mirascope.openai.prompt.OpenAIPrompt.stream) method to stream a response. All this is doing is setting `stream=True` and providing the [`OpenAIChatCompletionChunk`](../api/openai/types.md#mirascope.openai.types.OpenAIChatCompletionChunk) convenience wrappers around the response chunks.

```python
import os
from mirascope import OpenAIPrompt, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class Recipe(OpenAIPrompt):
	"""
	Recommend recipes that use {ingredient} as an ingredient
	"""
	
	ingredient: str
	
	call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


recipe = Recipe(ingredient="apples")
stream = recipe.stream()

for chunk in stream:
	print(str(chunk), end="")
```

### Async

If you want concurrency, you can use the `async` function instead.

```python
import os

from mirascope import OpenAIPrompt, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class Recipe(OpenAIPrompt):
	"""
	Recommend recipes that use {ingredient} as an ingredient
	"""

	ingredient: str
	
	call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


async def stream_recipe_recommendation():
    """Asynchronously streams the response for a call to the model using `OpenAIPrompt`."""
	recipe = Recipe(ingredient="apples")
	stream = recipe.async_stream()
    async for chunk in astream:
        print(chunk, end="")

asyncio.run(stream_recipe_recommendation())
```

### OpenAIChatCompletionChunk

The `stream` method returns an [`OpenAIChatCompletionChunk`](../api/openai/types.md#mirascope.openai.types.OpenAIChatCompletionChunk) instance, which is a convenience wrapper around the [`ChatCompletionChunk`](https://platform.openai.com/docs/api-reference/chat/streaming) class in `openai`

```python
from mirascope.openai.types import OpenAIChatCompletionChunk

chunk = OpenAIChatCompletionChunk(...)

chunk.chunk    # ChatCompletionChunk(...)
str(chunk)     # original.choices[0].delta.content
chunk.choices  # original.choices
chunk.choice   # original.choices[0]
chunk.delta    # original.choices[0].delta
chunk.content  # original.choices[0].delta.content
```
