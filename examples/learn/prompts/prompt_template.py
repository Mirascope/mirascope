from mirascope.core import BasePrompt, prompt_template


@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt)
# > Recommend a fantasy book
