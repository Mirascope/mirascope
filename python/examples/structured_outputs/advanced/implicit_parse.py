import json

from pydantic import BaseModel

from mirascope import llm


# We do not use the @llm.format decorator, but since Book has a parse classmethod,
# it will default to parse mode.
class Book(BaseModel):
    title: str
    author: str

    @classmethod
    def parse(cls, response: llm.Response, *args, **kwargs) -> "Book":
        """Parse JSON response into a Book instance."""
        print("Using custom parser.")
        data = json.loads(str(response))
        return cls(title=data["title"], author=data["author"])

    @classmethod
    def formatting_instructions(cls) -> str:
        return f"""
        For your final response, output ONLY a valid JSON dict (NOT THE SCHEMA).
        It must adhere to this schema:
        {json.dumps(cls.model_json_schema(), indent=2)}
        """


@llm.call("openai:gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


def main():
    response: llm.Response[Book] = recommend_book("fantasy")
    response.format()
    # Output: > Using custom parser.


if __name__ == "__main__":
    main()
