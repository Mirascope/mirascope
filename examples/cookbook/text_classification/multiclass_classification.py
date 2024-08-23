from enum import Enum

from mirascope.core import openai, prompt_template


class Sentiment(Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


@openai.call("gpt-4o-mini", response_model=Sentiment)
@prompt_template(
    """
    Classify the sentiment of the following text: {text}
    """
)
def classify_sentiment(text: str): ...


text = "I hate this product. It's terrible."
label = classify_sentiment(text)
assert label == Sentiment.NEGATIVE

text = "I don't feel strongly about this product."
label = classify_sentiment(text)
assert label == Sentiment.NEUTRAL

text = "I love this product. It's amazing!"
label = classify_sentiment(text)
assert label == Sentiment.POSITIVE
