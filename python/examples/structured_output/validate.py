from pydantic import BaseModel, field_validator

from mirascope import llm


class BookRecommendation(BaseModel):
    title: str
    year: int

    @field_validator("year")
    @classmethod
    def must_be_recent(cls, v: int) -> int:
        if v < 2020:
            raise ValueError(f"Must be published after 2020, got {v}")
        return v


@llm.call("openai/gpt-4o-mini", format=BookRecommendation)
def recommend_book():
    return "Recommend a science fiction book."


response = recommend_book()
book, response = response.validate()  # Retries once if validation fails
print(f"{book.title} ({book.year})")
