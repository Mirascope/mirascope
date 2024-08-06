"""Basic example using an @gemini.call to stream a call."""

from google.generativeai import configure  # type: ignore

from mirascope.core import gemini

configure(api_key="YOUR_GEMINI_API_KEY")


@gemini.call(model="gemini-1.0-pro", stream=True)
def recommend_book(genre: str):
    """Recommend a {genre} book."""


results = recommend_book(genre="fiction")
for chunk, _ in results:
    print(chunk.content, end="", flush=True)
    # > Certainly! If you're looking for a compelling fiction book, I highly recommend
    #   "The Night Circus" by Erin Morgenstern. ...
print(results.cost)
# > None
print(results.message_param)
# > {'role': 'model', 'parts': [text: "**Literary Fiction:**\n\n* **The ..."]}
print(results.user_message_param)
# > {'parts': ['Recommend a fiction book.'], 'role': 'user'}
