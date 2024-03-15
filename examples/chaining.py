"""
Chaining multiple calls together for Chain of Thought (CoT) is as simple as writing a
function:
"""
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

    call_params = OpenAICallParams(model="gpt-4")

    @cached_property  # !!! so multiple access doesn't make multiple calls
    def chef(self) -> str:
        """Uses `ChefSelector` to select the chef based on the food type."""
        return ChefSelector(food_type=self.food_type).call().content


response = RecipeRecommender(food_type="japanese", ingredient="apples").call()
print(response.content)
# > Certainly! Here's a recipe for a delicious and refreshing Japanese Apple Salad: ...
