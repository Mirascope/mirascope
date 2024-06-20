"""Basic example using an @openai_stream to stream a call."""
import os

from mirascope.core.openai import openai_stream

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai_stream(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book."""


results = recommend_book(genre="fiction")
for chunk, _ in results:
    print(chunk.content, end="", flush=True)
    # > Certainly! If you're looking for a compelling fiction book, I highly recommend
    #   "The Night Circus" by Erin Morgenstern. ...
print(results.cost)
print(results.message_param)
# > {
#       "content": 'Certainly! If you haven\'t read it yet, I highly recommend "The Night Circus" by Erin Morgenstern. ...',
#       "role": "assistant",
#       "tool_calls": None,
#   }
print(results.user_message_param)
# > {"content": "Recommend a fiction book.", "role": "user"}
