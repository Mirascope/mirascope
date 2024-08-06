from enum import Enum

from pydantic import BaseModel

from mirascope.core import openai, prompt_template


class Sentiment(Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class SentimentWithReasoning(BaseModel):
    reasoning: str
    sentiment: Sentiment


@openai.call("gpt-4o-mini", response_model=SentimentWithReasoning)
@prompt_template(
    """
    Classify the sentiment of the following text: {text}.
    Explain your reasoning for the classified sentiment.
    """
)
def classify_sentiment_with_reasoning(text: str): ...


text = "I would recommend this product if it were cheaper..."
response = classify_sentiment_with_reasoning(text)
print(response.sentiment)
# > Sentiment.NEUTRAL
print(f"Reasoning: {response.reasoning}")
# > Reasoning: The statement expresses a conditional recommendation that is
#   dependent on the price of the product. While the speaker has a positive
#   inclination to recommend the product, the condition of it being cheaper
#   introduces a level of uncertainty, leading to a neutral sentiment overall.
