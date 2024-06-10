"""Automatically formatted list types

Each item in the list will be new lined.
"""
from mirascope import BasePrompt


class BookRecommendations(BasePrompt):
    prompt_template = """
    Can you recommend some books on the following topics?
    {topics}
    """

    topics: list[str]


book_recommendations = BookRecommendations(topics=["coding", "music"])
print(book_recommendations.messages())
# > [
#        {
#            "role": "user",
#            "content": "Can you recommend some books on the following topics?\ncoding\nmusic",
#        }
#   ]
print(book_recommendations)
# > Can you recommend some books on the following topics?
#   coding
#   music
print(book_recommendations.dump())
# > {
#        "tags": [],
#        "template": "Can you recommend some books on the following topics?\n{topics}",
#        "inputs": {"topics": ["coding", "music"]},
#   }
