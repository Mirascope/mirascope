from mirascope.core import BasePrompt, metadata, prompt_template


@metadata({"tags": {"version:0001", "category:books"}})
@prompt_template("Recommend a {genre} book for a {age_group} reader.")
class BookRecommendationPrompt(BasePrompt):
    genre: str
    age_group: str


prompt = BookRecommendationPrompt(genre="fantasy", age_group="adult")
print(prompt.dump()["metadata"])
# > {'tags': {'version:0001', 'category:books'}}
