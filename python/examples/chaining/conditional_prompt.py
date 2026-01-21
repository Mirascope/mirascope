from enum import Enum

from mirascope import llm


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


@llm.prompt(format=Sentiment)
def classify_sentiment(review: str):
    return f"Is the following review positive or negative? {review}"


@llm.prompt
def respond_to_review(review: str, sentiment: Sentiment):
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
sentiment = classify_sentiment("openai/gpt-5-mini", positive_review).parse()
response = respond_to_review("openai/gpt-5-mini", positive_review, sentiment)
print(response.text())
