"""Basic example using an @openai.call to stream a call."""

import os

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai.call(model="gpt-4o", stream=True)
def recommend_book(genre: str):
    """Recommend a {genre} book."""


results = recommend_book(genre="fiction")
for chunk, _ in results:
    print(chunk.content, end="", flush=True)
    # > Certainly! If you're looking for a compelling fiction book, I highly recommend
    #   "The Night Circus" by Erin Morgenstern. ...
print(results.cost)
# > 0.0018
print(results.message_param)
# > {
#       "content": 'Certainly! If you haven\'t read it yet, I highly recommend "The Night Circus" by Erin Morgenstern. ...',
#       "role": "assistant",
#       "tool_calls": None,
#   }
print(results.user_message_param)
# > {"content": "Recommend a fiction book.", "role": "user"}
