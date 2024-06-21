"""
This example demonstrates how to chain functions in parallel using the `call_async` decorator.
"""

import asyncio
import os

from pydantic import BaseModel

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai.call_async(model="gpt-3.5-turbo")
async def chef_selector(ingredient: str) -> str:
    """
    Please identify a chef who is well known for cooking with {ingredient}.
    Respond only with the chef's name.
    """


class IngredientsList(BaseModel):
    ingredients: list[str]


@openai.call_async(model="gpt-3.5-turbo", response_model=IngredientsList)
async def ingredient_identifier(ingredient: str) -> IngredientsList:
    """
    Given a base ingredient {ingredient}, return a list of complementary ingredients.
    Make sure to exclude the original ingredient from the list.
    """


@openai.call_async(model="gpt-3.5-turbo")
async def recipe_recommender(ingredient: str) -> openai.OpenAICallFunctionReturn:
    """
    SYSTEM:
    Your task is to recommend a recipe. Pretend that you are chef {chef}.

    USER:
    Recommend recipes that use the following ingredients:
    {ingredients}
    """
    chef = await chef_selector(ingredient=ingredient)
    ingredients = await ingredient_identifier(ingredient=ingredient)
    return {
        "computed_fields": {
            "chef": chef.content,
            "ingredients": ingredients.ingredients,
        }
    }


async def run():
    response = await recipe_recommender(ingredient="apples")
    print(response.content)


asyncio.run(run())
