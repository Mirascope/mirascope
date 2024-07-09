
# Text Classification

This recipe shows how to use LLMs -- in this case, the OpenAI API -- to perform text classification tasks. It will demonstrate both binary classification and multi-class classification.

!!! info

    Text Classification is a classic task in Natural Language Processing (NLP), including e.g. spam detection, sentiment analysis, and many more. Large Language Models (LLMs) make these tasks easier to implement than ever before, requiring just an API call and some prompt engineering.

## Binary Classification

For binary classification, we can classify text as `True/False` (`0/1`) by extracting a boolean value. We can do this by setting `response_model=bool` and prompting the model to classify to the desired label:

```python
from mirascope.core import openai


@openai.call("gpt-4o", response_model=bool)
def classify_spam(text: str):
    """Classify the following text as spam or not spam: {text}"""


text = "Would you like to buy some cheap viagra?"
label = classify_spam(text)
assert label is True

text = "Hi! It was great meeting you today. Let's stay in touch!"
label = classify_spam(text)
assert label is False
```

It's actually that simple.

## Multi-Class Classification

For multi-class classification, we can use an `Enum` to define our labels:

```python
from enum import Enum


class Sentiment(Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
```

Then we just set `response_model=Sentiment` to analyze the sentiment of the given text:

```python
@openai.call("gpt-4o", response_model=Sentiment)
def analyze_sentiment(text: str):
    """Classify the sentiment of the following text: {text}"""


text = "I hate this product. It's terrible."
label = analyze_sentiment(text)
assert label == Sentiment.NEGATIVE

text = "I don't feel strongly about this product."
label = analyze_sentiment(text)
assert label == Sentiment.NEUTRAL

text = "I love this product. It's amazing!"
label = analyze_sentiment(text)
assert label == Sentiment.POSITIVE
```

In this recipe, we've shown how to use simpler types like `bool` and `Enum` to classify text, but you can also set `response_model` to more complex Pydantic `BaseModel` definitions to extract not just the label but also additional information such as the reasonining for the label. Check out the [`response_model` usage documentation](../learn/response_models.md) for more information.
