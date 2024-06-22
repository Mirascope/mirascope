"""Basic example using an @gemini.call to make a call."""

from google.generativeai import configure  # type: ignore

from mirascope.core import gemini

configure(api_key="YOUR_GEMINI_API_KEY")


@gemini.call(model="gemini-1.0-pro")
def recommend_book(genre: str):
    """Recommend a {genre} book."""


results = recommend_book(genre="fiction")
print(results.content)
# > **Literary Fiction:**
# >
# > * **The Overstory** by Richard Powers: An ambitious and thought-provoking novel ...
print(results.cost)
# > None
print(results.usage)
# > None
print(results.message_param)
# > {'role': 'model', 'parts': [text: "**Literary Fiction:**\n\n* **The ..."]}
print(results.user_message_param)
# > {'parts': ['Recommend a fiction book.'], 'role': 'user'}
