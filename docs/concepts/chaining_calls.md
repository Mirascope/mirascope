# Chaining Calls

To achieve better results, it is often worth splitting up a large task into multiple subtasks (LLM calls) that can be chained together. While some chains can be simple, chains for more difficult tasks can quickly become complex. With Mirascope, you have the option of chaining calls directly, but we recommend using properties to give you the power of caching previous responses as well as colocating all inputs into one prompt - this is extremely important as chains get more complex. Either way, we give you full control over how you construct your chains.

## Chaining using properties (recommended)

To take full advantage of Mirascope's classes, we recommend writing chains using properties. This provides a clean way of writing complex chains where each call depends on the previous call in the chain, allowing you to call the entire chain at once while specifying every input simultaneously. In addition, you can use the `@cached_property` decorator to cache the result of each call as well as the `@computed_field` decorator to include the output at every step of the chain in the final dump.

```python
import os
from functools import cached_property

from mirascope.openai import OpenAICall
from pydantic import computed_field

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class ChefSelector(OpenAICall):
    prompt_template = """
    Name a chef who is really good at cooking {food_type} food.
    Give me just the name.
    """

    food_type: str


class RecipeRecommender(ChefSelector):
    prompt_template = """
    SYSTEM:
    Imagine that you are chef {chef}.
    Your task is to recommend recipes that you, {chef}, would be excited to serve.

    USER:
    Recommend a recipe using {ingredient}.
    """

    ingredient: str

    @computed_field
    @cached_property
    def chef(self) -> str:
        """Uses `ChefSelector` to select the chef based on the food type."""
        return ChefSelector(food_type=self.food_type).call().content


recommender = RecipeRecommender(food_type="japanese", ingredient="apples")
recipe = recommender.call()
print(recipe.content)
# > Certainly! Here's a recipe for a delicious and refreshing Japanese Apple Salad: ...
```

And, since we used the `@computed_field` decorator, we can see the entire chain in the dump:

```python
print(recommender.dump())
#> {
#>   "tags": [],
#>   "template": "SYSTEM:\nImagine that you are chef {chef}.\nYour task is to recommend recipes that you,
#>     {chef}, would be excited to serve.\n\nUSER:\nRecommend a recipe using {ingredient}.",
#>   "inputs": {
#>     "food_type": "japanese",
#>     "ingredient": "apples",
#>     "chef": "Masaharu Morimoto"
#>   }
#> }
```

## Chaining directly (function chaining)

In a pinch, nothing is stopping you from making one call, then passing the output of that call into the next call. For simple use cases, this "brute force" method can be the easiest way to chain calls; however, you miss out on the ability to cache previous responses to save on time and token usage as well as colocating all inputs along the chain into one prompt.

```python
import os

from mirascope.openai import OpenAICall, OpenAICallParams

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class ChefSelector(OpenAICall):
    prompt_template = """
    Name a chef who is really good at cooking {food_type} food.
    Give me just the name.
    """

    food_type: str


class RecipeRecommender(OpenAICall):
    prompt_template = """
    SYSTEM:
    Imagine that you are chef {chef}.
    Your task is to recommend recipes that you, {chef}, would be excited to serve.

    USER:
    Recommend a recipe using {ingredient}.
    """

    chef: str
    ingredient: str


selector = ChefSelector(food_type="japanese")
chef = selector.call().content
print(chef)
#> Masaharu Morimoto.

recommender = RecipeRecommender(chef=chef, ingredient="apples")
recipe = recommender.call().content
print(recipe)
#> Certainly! Here's a recipe for a delicious and refreshing Wagyu Beef and Apple roll: ...
```

!!! note

    For reusability, you can always wrap the chain flow in a function like you would for any other functions, e.g.

    ```python
    def recommend_recipe(food_type: str, ingredient: str) -> str:
        chef = ChefSelector(food_type="japanese").call().content
        return  RecipeRecommender(chef=chef, ingredient="apples").call().content
    ```

While this works, we cannot see the initial input of `food_type="japanese"` from the dump of the final call. If you plan on logging your results, you would have to inefficiently log every call along the chain to see all relevant inputs.

```python
print(recommender.dump())
#> {
#>    "tags": [],
#>    "template": "SYSTEM:\nImagine that you are chef {chef}.\nYour task is to recommend recipes that you,
#>      {chef}, would be excited to serve.\n\nUSER:\nRecommend a {food_type} recipe using {ingredient}.",
#>    "inputs": {
#>      "chef": "Masaharu Morimoto.",
#>      "ingredient": "apples"
#>    }
#> }
```
