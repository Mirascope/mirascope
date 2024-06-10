"""
Basic example using an OpenAICall to make a call
"""

import os

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


response = BookRecommender(genre="fantasy").call()
print(response.content)
# > Certainly! If you're looking for a captivating fantasy read, I highly recommend "The Name of the Wind" by Patrick Rothfuss. It's the first book in the "Kingkiller Chronicle" series. The story follows the life of Kvothe, a legendary figure known for his magical abilities and adventurous exploits, as he recounts his journey from a gifted but troubled youth to a renowned hero and powerful magician. Rothfuss's writing is lyrical and immersive, and the world-building is incredibly rich. This book is perfect for anyone who loves detailed storytelling, complex characters, and a bit of mystery.
print(response.cost)
# > 0.00185
print(response.usage)
# > CompletionUsage(completion_tokens=119, prompt_tokens=13, total_tokens=132)
print(response.message)
# > ChatCompletionMessage(content='Certainly! If you\'re looking for a captivating fantasy read, I highly recommend "The Name of the Wind" by Patrick Rothfuss. It\'s the first book in the "Kingkiller Chronicle" series. The story follows the life of Kvothe, a legendary figure known for his magical abilities and adventurous exploits, as he recounts his journey from a gifted but troubled youth to a renowned hero and powerful magician. Rothfuss\'s writing is lyrical and immersive, and the world-building is incredibly rich. This book is perfect for anyone who loves detailed storytelling, complex characters, and a bit of mystery.', role='assistant', function_call=None, tool_calls=None)
print(response.user_message_param)
# > {'content': 'Please recommend a fantasy book.', 'role': 'user'}
