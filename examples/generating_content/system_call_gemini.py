"""A GeminiCall example.

Gemini uses a different pattern for system calls. Rather than
having a SYSTEM, and ASSISTANT, you have MODEL and USER.
"""
from google.generativeai import configure

from mirascope.gemini import GeminiCall, GeminiCallParams

configure(api_key="YOUR_GEMINI_API_KEY")


class RecipeRecommender(GeminiCall):
    prompt_template = """
    USER: 
    You are the world's greatest chef.

    MODEL:
    I am the world's greatest chef.

    USER: 
    Can you recommend some recipes that use {ingredient} as an ingredient?
    """

    ingredient: str

    call_params = GeminiCallParams(model="gemini-1.0-pro")


recipes = RecipeRecommender(ingredient="chicken").call()
print(recipes.content)
# > 1. **Honey Garlic Chicken**: This dish is a classic for a reason. The chicken is marinated in a mixture of honey, garlic, soy sauce, and ginger, then cooked until it is golden brown and sticky. Serve over rice or noodles.
#   ...
