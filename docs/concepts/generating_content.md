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


class RecipeRecommender(OpenAIPrompt):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


response = RecipeRecommender(ingredient="apples").call()
print(response.content)  # prints the string content of the call
```

The `call_params` of the OpenAI client is tied to the call (and thereby the prompt). Refer to Engineering better prompts [Add link] for more information.

### Async

If you are want concurrency, you can use the `async` function instead.

```python
import asyncio
import os

from mirascope import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class RecipeRecommender(OpenAIPrompt):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


async def recommend_recipes():
    """Asynchronously calls the model using `OpenAICall` to generate a recipe."""
    return await RecipeRecommender(ingredient="apples").call_async()


print(asyncio.run(recommend_recipes())) 
```

### CallResponse

The `call` method returns an [`OpenAICallResponse`](../api/openai/types.md#mirascope.openai.types.OpenAICallResponse) class instance, which is a simple wrapper around the [`ChatCompletion`](https://platform.openai.com/docs/api-reference/chat/object) class in `openai` that extends [`BaseCallResponse`](../api/base/types.md#mirascope.base.types.BaseCallResponse). In fact, you can access everything from the original response as desired. The primary purpose of the class is to provide convenience.

```python
from mirascope.openai.types import OpenAICallResponse

response = OpenAICallResponse(...)

completion.content     # original.choices[0].message.content
completion.tool_calls  # original.choices[0].message.tool_calls
completion.message     # original.choices[0].message
completion.choice      # original.choices[0]
completion.choices     # original.choices
response.response      # ChatCompletion(...)
```

### Chaining Calls

To achieve better results, it is often worth splitting up a large task into multiple subtasks that can be chained together. While some chains can be simple, chains for more difficult tasks can quickly become complex. With Mirascope, chaining calls together is as simple as writing properties and/or functions, giving you full control over how you construct your chains. This is extremely important as chains get more complex.

#### Chaining Using Properties

To take full advantage of Mirascope's classes, we recommend writing chains using properties. This provides a clean way of writing even complex chains where each call depends on the previous call in the chain. You can write arbitrarily long chains while maintaining full control and access to every aspect of the chain -- all the way down to every local variable. No additional classes are necessary to gain such access.

```python
import os
from functools import cached_property

from mirascope.openai import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class ChefSelector(OpenAICall):
    prompt_template = "Name a chef who is really good at cooking {food_type} food"

    food_type: str

    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


class RecipeRecommender(ChefSelector):
    prompt_template = """
    SYSTEM:
    Imagine that you are chef {chef}.
    Your task is to recommend recipes that you, {chef}, would be excited to serve.

    USER:
    Recommend a {food_type} recipe using {ingredient}.
    """

    ingredient: str

    @cached_property
    def chef(self) -> str:
        """Uses `ChefSelector` to select the chef based on the food type."""
        return ChefSelector(food_type=self.food_type).call().content


response = RecipeRecommender(food_type="japanese", ingredient="apples").call()
print(response.content)
# > Certainly! Here's a recipe for a delicious and refreshing Japanese Apple Salad: ...
```

#### Chaining Using Functions

You can also chain calls together like you would any normal chain of functions in Python. This is not reusable out of the box like chaining with properties, but it's easy enough to wrap the chain in a function for reusability as necessary:

```python
import os

from mirascope.openai import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class ChefSelector(OpenAICall):
    prompt_template = "Name a chef who is really good at cooking {food_type} food"

    food_type: str

    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


class RecipeRecommender(ChefSelector):
    prompt_template = """
    SYSTEM:
    Imagine that you are chef {chef}.
    Your task is to recommend recipes that you, {chef}, would be excited to serve.

    USER:
    Recommend a {food_type} recipe using {ingredient}.
    """

    chef: str
    food_type: str
    ingredient: str


def recommend_recipe(food_type: str, ingredient: str) -> str:
    """Generates a recipe recommendation for `food_type` using `ingredient`."""
    selector = ChefSelector(food_type=food_type)
    chef = selector.call().content
    recommender = RecipeRecommender(chef=chef, food_type=food_type, ingredient=ingredient)
    return recommender.call().content


recipe = recommend_recipe(food_type="japanese", ingredient="apples")
print(recipe)
# > Certainly! Here's a recipe for a delicious and refreshing Wagyu Beef and Apple roll: ...
```
