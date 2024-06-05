from enum import Enum
from functools import cached_property

from pydantic import computed_field

from mirascope.openai import OpenAICall, OpenAIExtractor


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class SentimentClassifier(OpenAIExtractor[Sentiment]):
    extract_schema: type[Sentiment] = Sentiment
    prompt_template = "Is the following review positive or negative? {review}"

    review: str


class ReviewResponder(OpenAICall):
    prompt_template = """
    SYSTEM:
    Your task is to respond to a review.
    The review has been identified as {sentiment}.
    Please write a {conditional_review_prompt}.

    USER: Write a response for the following review: {review}
    """

    review: str

    @property
    def conditional_review_prompt(self) -> str:
        if self.sentiment == Sentiment.POSITIVE:
            return "thank you response for the review."
        else:
            return "reponse addressing the review."

    @computed_field  # type: ignore[misc]
    @cached_property
    def sentiment(self) -> Sentiment:
        classifier = SentimentClassifier(review=self.review)
        return classifier.extract()


positive_review = "This tool is awesome because it's so flexible!"
responder = ReviewResponder(review=positive_review)
response = responder.call()
print(f"Sentiment: {responder.sentiment}")  # positive
print(f"Positive Response: {response.content}")

negative_review = "This product is terrible and too expensive!"
responder.__dict__.pop("sentiment", None)  # remove from cache
responder.review = negative_review
response = responder.call()
print(f"Sentiment: {responder.sentiment}")  # negative
print(f"Negative Response: {response.content}")
