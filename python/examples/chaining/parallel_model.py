import asyncio

from mirascope import llm

model = llm.model("openai/gpt-5-mini")


async def chef_selector(ingredient: str):
    return await model.call_async(
        f"Identify a chef known for cooking with {ingredient}. Return only their name."
    )


async def ingredients_identifier(ingredient: str):
    return await model.call_async(
        f"List 5 ingredients that complement {ingredient}.",
        format=list[str],
    )


async def recommend(chef: str, ingredients: list[str]):
    return await model.call_async(
        f"As chef {chef}, recommend a recipe using: {ingredients}"
    )


async def recipe_recommender(ingredient: str) -> str:
    chef_response, ingredients_response = await asyncio.gather(
        chef_selector(ingredient),
        ingredients_identifier(ingredient),
    )
    response = await recommend(chef_response.text(), ingredients_response.parse())
    return response.text()


async def main():
    recipe = await recipe_recommender("apples")
    print(recipe)


asyncio.run(main())
