# LLM Convenience Wrappers

Mirascope provides convenience wrappers around the OpenAI client to make writing the code even more enjoyable. We purposefully pass `**kwargs` through our calls so that you always have direct access to their arguments.

## Why should you care?

- Easy to learn
		- There's no magic here -- it's just python
		- Chaining is no different from writing basic python functions
- Convenient
		- You could do it yourself -- and you still can -- but there's just something nice about calling `str(res)` to get the response content
		- You only need to pass in a [`Prompt`](../api/prompts.md) and we'll handle the rest

## OpenAIChat

You can initialize an [`OpenAIChat`](../api/chat/models.md#mirascope.chat.models.OpenAIChat) instance and call [`create`](../api/chat/models.md#mirascope.chat.models.OpenAIChat.create) to generate an [`OpenAIChatCompletion`](../api/chat/types.md#mirascope.chat.types.OpenAIChatCompletion):

```python
from mirascope import OpenAIChat, Prompt

class RecipePrompt(Prompt):
	"""
	Recommend recipes that use {ingredient} as an ingredient
	"""

	ingredient: str

chat = OpenAIChat(api_key="YOUR_OPENAI_API_KEY")
res = chat.create(RecipePrompt(ingredient="apples"))
str(res)  # returns the string content of the completion
```

### Chaining

Adding a chain of calls is as simple as writing a function:

```python
class ChefPrompt(Prompt):
    """
    Name the best chef in the world at cooking {food_type} food
    """

    food_type: str


class RecipePrompt(Prompt):
    """
    Recommend a recipe that uses {ingredient} as an ingredient
    that chef {chef} would serve in their restuarant
    """

    ingredient: str
    chef: str


def recipe_by_chef_using(ingredient: str, food_type: str) -> str:
    """Returns a recipe using `ingredient`.

    The recipe will be generated based on what dish using `ingredient`
    the best chef in the world at cooking `food_type` might serve in
    their restaurant
    """
    chat = OpenAIChat(api_key="YOUR_OPENAI_API_KEY")
    chef_prompt = ChefPrompt(food_type=food_type)
    chef = str(chat.create(chef_prompt))
    recipe_prompt = RecipePrompt(ingredient=ingredient, chef=chef)
    return str(chat.create(recipe_prompt))


recipe = recipe_by_chef_using("apples", "japanese")
```

### Streaming

You can use the [`stream`](../api/chat/models.md#mirascope.chat.models.OpenAIChat.stream) method to stream a response. All this is doing is setting `stream=True` and providing the [`OpenAIChatCompletionChunk`](../api/chat/types.md#mirascope.chat.types.OpenAIChatCompletionChunk) convenience wrappers around the response chunks.

```python
chat = OpenAIChat()
stream = chat.stream(prompt)
for chunk in stream:
		print(str(chunk), end="")
```

## OpenAIChatCompletion

The [`OpenAIChatCompletion`](../api/chat/types.md#mirascope.chat.types.OpenAIChatCompletion) class is a simple wrapper around the [`ChatCompletion`](https://platform.openai.com/docs/api-reference/chat/object) class in `openai`. In fact, you can access everything from the original chunk as desired. The primary purpose of the class is to provide convenience.

```python
from mirascope.chat.types import OpenAIChatCompletion

completion = OpenAIChatCompletion(...)

completion.completion  # ChatCompletion(...)
str(completion)        # original.choices[0].delta.content
completion.choices     # original.choices
completion.choice      # original.choices[0]
completion.message     # original.choices[0].message
completion.content     # original.choices[0].message.content
```

## OpenAIChatCompletionChunk

Similarly the [`OpenAIChatCompletionChunk`](../api/chat/types.md#mirascope.chat.types.OpenAIChatCompletionChunk) is a convenience wrapper around the [`ChatCompletionChunk`](https://platform.openai.com/docs/api-reference/chat/streaming) class in `openai`

```python
from mirascope.chat.types import OpenAIChatCompletionChunk

chunk = OpenAIChatCompletionChunk(...)

chunk.chunk    # ChatCompletionChunk(...)
str(chunk)     # original.choices[0].delta.content
chunk.choices  # original.choices
chunk.choice   # original.choices[0]
chunk.delta    # original.choices[0].delta
chunk.content  # original.choices[0].delta.content
```

### Future updates

There is a lot more to be added to the Mirascope models. Here is a list in no order of things we are thinking about adding next: 

* tools as functions - decorator to write tools like normal functions
* additional models - support models beyond OpenAI

If you want some of these features implemented or if you think something is useful but not on this list, let us know!
