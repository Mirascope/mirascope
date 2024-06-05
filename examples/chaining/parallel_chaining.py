from functools import cached_property

from pydantic import computed_field

from mirascope.openai import OpenAICall, OpenAIExtractor


class ChefSelector(OpenAICall):
    prompt_template = """
    Please identify a chef who is well known for cooking with {ingredient}.
    Respond only with the chef's name.
    """

    ingredient: str


class IngredientIdentifier(OpenAIExtractor[list]):
    extract_schema: type[list] = list[str]
    prompt_template = """
    Given a base ingredient {ingredient}, return a list of complementary ingredients.
    Make sure to exclude the original ingredient from the list.
    """

    ingredient: str


class RecipeRecommender(ChefSelector):
    prompt_template = """
    SYSTEM:
    Your task is to recommend a recipe. Pretend that you are chef {chef}.

    USER:
    Recommend recipes that use the following ingredients:
    {ingredients}
    """

    @computed_field
    @cached_property
    def chef(self) -> str:
        response = ChefSelector(ingredient=self.ingredient).call()
        return response.content

    @computed_field
    @cached_property
    def ingredients(self) -> list[str]:
        identifier = IngredientIdentifier(ingredient=self.ingredient)
        return identifier.extract() + [self.ingredient]


recommender = RecipeRecommender(ingredient="apples")
response = recommender.call()
print(response.content)
