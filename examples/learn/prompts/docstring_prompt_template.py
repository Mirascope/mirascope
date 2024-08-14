import os

from mirascope.core import BasePrompt, openai

# Enable docstring prompt templates
os.environ["MIRASCOPE_DOCSTRING_PROMPT_TEMPLATE"] = "ENABLED"


class BookRecommendationPrompt(BasePrompt):
    """Recommend a {genre} book"""

    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt)
# > Recommend a fantasy book


@openai.call(model="gpt-4o-mini")
def recommend_book(genre: str):
    """Recommend a {genre} book"""
    ...


response = recommend_book("mystery")
print(response.content)
# > Here's a recommendation for a fantasy book: ...
