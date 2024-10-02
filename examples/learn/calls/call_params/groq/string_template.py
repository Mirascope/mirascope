from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-70b-versatile", call_params={"max_tokens": 512})
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
