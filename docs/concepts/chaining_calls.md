# Chaining Calls

To achieve better results, it is often worth splitting up a large task into multiple subtasks that can be chained together. While some chains can be simple, chains for more difficult tasks can quickly become complex. With Mirascope, chaining calls together is as simple as writing properties and/or functions, giving you full control over how you construct your chains. This is extremely important as chains get more complex.

## Chaining Using Properties

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

## Chaining Using Functions

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
