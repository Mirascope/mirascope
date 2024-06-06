from functools import cached_property

from pydantic import computed_field

from mirascope.openai import OpenAICall


# Step 1: Identify a Chef
class ChefSelector(OpenAICall):
    prompt_template = "Name a chef who is really good at cooking {food_type} food"

    food_type: str


# Step 2: Recommend Recipes
class RecipeRecommender(ChefSelector):
    prompt_template = """
    Imagine that you are chef {chef}.
    Recommend a {food_type} recipe using {ingredient}.
    """

    ingredient: str

    @computed_field  # type: ignore[misc]
    @cached_property
    def chef(self) -> str:
        """Uses `ChefSelector` to select the chef based on the food type."""
        return ChefSelector(food_type=self.food_type).call().content


recommender = RecipeRecommender(ingredient="apples", food_type="japanese")
response = recommender.call()
print(response.content)
