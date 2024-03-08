# Generating content

Now that you have your prompt, you can combine it with a model to generate content. Mirascope provides high-level wrappers around common providers so you can focus on prompt engineering instead of learning the interface for providers. Our high-level wrappers are not required to use our prompts but simply provide convenience if you wish to use it.

!!! note

    This doc uses OpenAI. See [using different model providers](using_different_model_providers.md) for how to generate content with other model providers like Anyscale, Together, Gemini, and more.

## OpenAIPrompt

[`OpenAIPrompt`](../api/openai/prompt.md#mirascope.openai.prompt.OpenAIPrompt) extends [`BasePrompt`](../api/base/prompt.md#mirascope.base.prompt.BasePrompt) by adding methods the OpenAI SDK provides such as `create`.

### Create

You can initialize an [`OpenAIPrompt`](../api/openai/prompt.md#mirascope.openai.prompt.OpenAIPrompt) instance and call the [`create`](../api/openai/prompt.md#mirascope.openai.prompt.OpenAIPrompt.create) method to generate an [`OpenAIChatCompletion`](../api/openai/types.md#mirascope.openai.types.OpenAIChatCompletion):

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
completion = recipe.create()
print(completion)  # prints the string content of the completion
```

The `call_params` of the OpenAI client is tied to the prompt. Refer to Engineering better prompts [Add link] for more information.

### Async

If you are want concurrency, you can use the `async` function instead.

```python
import asyncio
import os

from mirascope import OpenAIPrompt, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class Recipe(OpenAIPrompt):
    """
    Recommend recipes that use {ingredient} as an ingredient
    """
    
    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


async def create_recipe_recommendation():
    """Asynchronously creates the response for a call to the model using `OpenAIPrompt`."""
    recipe = Recipe(ingredient="apples")
    return await recipe.create()


print(asyncio.run(create_recipe_recommendation())) 
```

### Completion

The `create` method returns an [`OpenAIChatCompletion`](../api/openai/types.md#mirascope.openai.types.OpenAIChatCompletion) class instance, which is a simple wrapper around the [`ChatCompletion`](https://platform.openai.com/docs/api-reference/chat/object) class in `openai`. In fact, you can access everything from the original chunk as desired. The primary purpose of the class is to provide convenience.

```python
from mirascope.openai.types import OpenAIChatCompletion

completion = OpenAIChatCompletion(...)

completion.completion  # ChatCompletion(...)
str(completion)        # original.choices[0].delta.content
completion.choices     # original.choices
completion.choice      # original.choices[0]
completion.message     # original.choices[0].message
completion.content     # original.choices[0].message.content
completion.tool_calls  # original.choices[0].message.tool_calls
```

### Chaining

Adding a chain of calls is as simple as writing a function:

```python
import os
from mirascope import OpenAIPrompt, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class Chef(OpenAIPrompt):
    """
    Name the best chef in the world at cooking {food_type} food
    """

    food_type: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-1106")


class Recipe(OpenAIPrompt):
    """
    Recommend a recipe that uses {ingredient} as an ingredient
    that chef {chef} would serve in their restuarant
    """

    ingredient: str
    chef: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-1106")


def recipe_by_chef_using(ingredient: str, food_type: str) -> str:
    """Returns a recipe using `ingredient`.

    The recipe will be generated based on what dish using `ingredient`
    the best chef in the world at cooking `food_type` might serve in
    their restaurant
    """
    chef_client = Chef(food_type=food_type)
    recipe_client = Recipe(ingredient=ingredient, chef=chef_client.create())
    return recipe_client.create()


recipe = recipe_by_chef_using("apples", "japanese")
```
