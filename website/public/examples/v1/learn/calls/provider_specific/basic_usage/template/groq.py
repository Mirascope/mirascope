from mirascope.core import groq, prompt_template

# [!code highlight:4]
@groq.call("llama-3.1-70b-versatile")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response: groq.GroqCallResponse = recommend_book("fantasy")
print(response.content)
