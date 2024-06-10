"""Introduction to Mirascope Prompts

You can access the messages array that will be passed in to the LLM call.
You can access the templated prompt
You can get the dump of the class for logging and debugging
"""
from mirascope import BasePrompt


class BookRecommendationPrompt(BasePrompt):
    prompt_template = "Can you recommend some books on {topic}?"

    topic: str


prompt = BookRecommendationPrompt(topic="coding")
print(prompt.messages())
# > [{'role': 'user', 'content': 'Can you recommend some books on coding?'}]
print(prompt)
# > Can you recommend some books on coding?
print(prompt.dump())
# > {
#     "tags": [],
#     "template": "Can you recommend some books on {topic}?",
#     "inputs": {"topic": "coding"},
#   }
