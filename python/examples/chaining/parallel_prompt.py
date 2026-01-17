import asyncio

from mirascope import llm

model = "openai/gpt-5-mini"


@llm.prompt
async def chef_selector(ingredient: str):
    return (
        f"Identify a chef known for cooking with {ingredient}. Return only their name."
    )


@llm.prompt(format=list[str])
async def ingredients_identifier(ingredient: str):
    return f"List 5 ingredients that complement {ingredient}."


@llm.prompt
async def recommend(chef: str, ingredients: list[str]):
    return f"As chef {chef}, recommend a recipe using: {ingredients}"


async def recipe_recommender(ingredient: str) -> str:
    chef_response, ingredients_response = await asyncio.gather(
        chef_selector(model, ingredient),
        ingredients_identifier(model, ingredient),
    )

    response = await recommend(
        model, chef_response.text(), ingredients_response.parse()
    )
    return response.text()


async def main():
    recipe = await recipe_recommender("apples")
    print(recipe)


asyncio.run(main())
