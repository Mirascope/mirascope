# Text Classification with LLMs

This recipe demonstrates how to leverage Large Language Models (LLMs) -- specifically the OpenAI API -- to perform text classification tasks. We'll cover both **binary classification**, **multi-class classification**, and **classification with reasoning**, providing you with the tools to tackle a wide range of real-world text analysis problems.

??? info "Key Concepts"

    - [Calls](ADD LINK)

    - [Response Model](ADD LINK)

!!! note "Background"

    Text Classification is a fundamental task in Natural Language Processing (NLP), with applications ranging from spam detection and sentiment analysis to content categorization and intent recognition. Large Language Models (LLMs) have revolutionized this field, making sophisticated classification tasks accessible through simple API calls and thoughtful prompt engineering.

## Setup

To set up our environment, first let's install all of the packages we will use:

```shell
pip install "mirascope[openai]"
```

Make sure to also set your `OPENAI_API_KEY` if you haven't already.

## Binary Classification

!!! note ""

    [binary_classification.py](ADD LINK)

Binary classification involves categorizing text into one of two classes. We'll demonstrate this by creating a spam detector that classifies text as either spam or not spam.

For binary classification, we can extract a boolean value by setting `response_model=bool` and prompting the model to classify the text:

```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini", response_model=bool)
@prompt_template(
    """
    Classify the following text as spam or not spam: {text}
    """
)
def classify_spam(text: str): ...


text = "Would you like to buy some cheap viagra?"
label = classify_spam(text)
assert label is True   # This text is classified as spam

text = "Hi! It was great meeting you today. Let's stay in touch!"
label = classify_spam(text)
assert label is False  # This text is classified as not spam
```

## Multi-Class Classification

!!! note ""

    [multiclass_classification.py](ADD LINK)

Multi-class classification extends the concept to scenarios where we need to categorize text into one of several classes. We'll demonstrate this with a sentiment analysis task.

First, we define an Enum to represent our sentiment labels:

```python
from enum import Enum


class Sentiment(Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
```

Then, we set `response_model=Sentiment` to analyze the sentiment of the given text:

```python
from mirascope.core import openai, prompt_template


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
```

## Classification with Reasoning

!!! note ""

    [classification_with_reasoning.py](ADD LINK)

So far we've demonstrated using simple types like `bool` and `Enum` for classification, but we can extend this approach using Pydantic's `BaseModel` class to extract additional information beyond just the classification label.

For example, we can gain insight to the LLMs reasoning for the classified label simply by including a `reasoning` field in our response model and updating the prompt:

```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel


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
```

## Handling Uncertainty

!!! note ""

    [handling_uncertainty.py](ADD LINK)

When dealing with LLMs for classification tasks, it's important to account for cases where the model might be uncertain about its prediction. We can modify our approach to include a certainty score and handle cases where the model's confidence is below a certain threshold.

```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel


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
```

!!! tip "Additional Real-World Examples"

    - Content Moderation: Classify user-generated content as appropriate, inappropriate, or requiring manual review.
    - Customer Support Triage: Categorize incoming support tickets by urgency or department.
    - News Article Categorization: Classify news articles into topics (e.g. politics, sports, technology, etc).
    - Intent Recognition: Identify user intent in chatbot interactions (e.g. make a purchase, ask for help, etc.).
    - Email Classification: Sort emails into categories like personal, work-related, promotional, or urgent.

When adapting this recipe to your specific use-case, consider the following:

- Refine your prompts to provide clear instructions and relevant context for your specific classification task.
- Experiment with different model providers and version to balance accuracy and speed.
- Implement error handling and fallback mechanisms for cases where the model's classification is uncertain.
- Consider using a combination of classifiers for more complex categorization tasks.
