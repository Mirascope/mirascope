from mirascope.core import google, prompt_template


@google.call(
    "gemini-1.5-flash",
    call_params={"config": {"max_output_tokens": 512}},
)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
