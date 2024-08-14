from pydantic import computed_field

from mirascope.core import BasePrompt, prompt_template


@prompt_template("Recommend a {genre} {book_type} for a {age_group} reader.")
class BookRecommendationPrompt(BasePrompt):
    genre: str
    age_group: str

    @computed_field
    @property
    def book_type(self) -> str:
        if self.age_group == "child":
            return "picture book"
        elif self.age_group == "young adult":
            return "novel"
        else:
            return "book"


prompt = BookRecommendationPrompt(genre="fantasy", age_group="child")
print(prompt)
# > Recommend a fantasy picture book for a child reader.
