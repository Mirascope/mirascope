"""NOTE: This example is under construction"""

import os
from enum import Enum

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


@openai.call(model="gpt-4o", response_model=Sentiment)
def sentiment_classifier(review: str):
    """Is the following review positive or negative? {review}"""


@openai.call()
def review_responder(
    review: str, sentiment: Sentiment
) -> openai.OpenAICallFunctionReturn:
    """
    SYSTEM:
    Your task is to respond to a review.
    The review has been identified as {sentiment}.
    Please write a {conditional_review_prompt}.

    USER: Write a response for the following review: {review}
    """
    conditional_review_prompt = (
        "thank you response for the review."
        if sentiment == Sentiment.POSITIVE
        else "reponse addressing the review."
    )
    sentiment = sentiment_classifier(review=review)

    {
        "computed_fields": {
            "conditional_review_prompt": conditional_review_prompt,
            "sentiment": sentiment,
        }
    }


positive_review = "This tool is awesome because it's so flexible!"
response = review_responder(review=positive_review)
print(response)
# print(f"Sentiment: {responser.sentiment}")  # positive
# print(f"Positive Response: {response.content}")

# negative_review = "This product is terrible and too expensive!"
# responder.__dict__.pop("sentiment", None)  # remove from cache
# responder.review = negative_review
# response = responder.call()
# print(f"Sentiment: {responder.sentiment}")  # negative
# print(f"Negative Response: {response.content}")
