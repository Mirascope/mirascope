from mirascope.core import BasePrompt, prompt_template


@prompt_template(
    """
    Recommend a book.
    It should be a {genre} book.
    """
)
class BookRecommendationPrompt(BasePrompt):
    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")
print(prompt)
# > Recommend a book.
#   It should be a fantasy book.
