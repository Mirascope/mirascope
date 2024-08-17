from mirascope.core import BasePrompt, prompt_template


@prompt_template("Recommend a {genre} book for a {age_group} reader")
class BookRecommendationPrompt(BasePrompt):
    genre: str
    age_group: str


prompt = BookRecommendationPrompt(genre="fantasy", age_group="young adult")
print(prompt)
# > Recommend a fantasy book for a young adult reader
print(prompt.message_params())
# > [BaseMessageParam(role="user", content="Recommend a fantasy book for a young adult reader")]
