from enum import Enum

from mirascope.core import openai, prompt_template


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


@openai.call(model="gpt-4o", response_model=Sentiment)
def sentiment_classifier(review: str) -> str:
    return f"Is the following review positive or negative? {review}"


@openai.call("gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    Your task is to respond to a review.
    The review has been identified as {sentiment}.
    Please write a {conditional_review_prompt}.

    USER: Write a response for the following review: {review}
    """
)
def review_responder(review: str) -> openai.OpenAIDynamicConfig:
    sentiment = sentiment_classifier(review=review)
    conditional_review_prompt = (
        "thank you response for the review."
        if sentiment == Sentiment.POSITIVE
        else "response addressing the review."
    )
    return {
        "computed_fields": {
            "conditional_review_prompt": conditional_review_prompt,
            "sentiment": sentiment,
        }
    }


positive_review = "This tool is awesome because it's so flexible!"
response = review_responder(review=positive_review)
print(response)
print(response.dynamic_config)
