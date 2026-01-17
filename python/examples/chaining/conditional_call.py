from enum import Enum

from mirascope import llm


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


@llm.call("openai/gpt-5-mini", format=Sentiment)
def classify_sentiment(review: str):
    return f"Is the following review positive or negative? {review}"


@llm.call("openai/gpt-5-mini")
def respond_to_review(review: str):
    sentiment = classify_sentiment(review).parse()

    if sentiment == Sentiment.POSITIVE:
        instruction = "Write a thank you response for the review."
    else:
        instruction = "Write a response addressing the concerns in the review."

    return f"""
    The review has been identified as {sentiment.value}.
    {instruction}

    Review: {review}
    """


positive_review = "This tool is awesome because it's so flexible!"
response = respond_to_review(positive_review)
print(response.text())
