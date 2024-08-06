from enum import Enum

from pydantic import BaseModel

from mirascope.core import openai, prompt_template


class Sentiment(Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class SentimentWithCertainty(BaseModel):
    sentiment: Sentiment
    reasoning: str
    certainty: float


@openai.call("gpt-4o-mini", response_model=SentimentWithCertainty)
@prompt_template(
    """
    Classify the sentiment of the following text: {text}
    Explain your reasoning for the classified sentiment.
    Also provide a certainty score between 0 and 1, where 1 is absolute certainty.
    """
)
def classify_sentiment_with_certainty(text: str): ...


text = "This is the best product ever. And the worst."
response = classify_sentiment_with_certainty(text)
if response.certainty > 0.8:
    print(f"Sentiment: {response.sentiment}")
    print(f"Reasoning: {response.reasoning}")
    print(f"Certainty: {response.certainty}")
else:
    print("The model is not certain enough about the classification.")
    # Handle the uncertainty (e.g., flag for human review, use a fallback method, etc.)
