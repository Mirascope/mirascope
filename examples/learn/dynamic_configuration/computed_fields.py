from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book with a reading level of {reading_level}")
def recommend_book(genre: str, age: int) -> openai.OpenAIDynamicConfig:
    reading_level = "adult"
    if age < 12:
        reading_level = "elementary"
    elif age < 18:
        reading_level = "young adult"
    return {"computed_fields": {"reading_level": reading_level}}


response = recommend_book("fantasy", 15)
print(response.content)
