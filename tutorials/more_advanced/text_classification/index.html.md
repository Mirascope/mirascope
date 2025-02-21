# Text Classification

In this recipe we’ll explore using Mirascope to implement binary classification, multi-class classification, and various other extensions of these classification techniques — specifically using Python the OpenAI API. We will also compare these solutions with more traditional machine learning and Natural Language Processing (NLP) techniques.


<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
    Text classification is a fundamental classification problem and NLP task that involves categorizing text documents into predefined classes or categories. Historically this has required training text classifiers through more traditional machine learning methods. Large Language Models (LLMs) have revolutionized this field, making sophisticated classification tasks accessible through simple API calls and thoughtful prompt engineering.
</p>
</div>

## Setup

Let's start by installing Mirascope and its dependencies:


```python
!pip install "mirascope[openai]"
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Binary Classification: Spam Detection

Binary classification involves categorizing text into one of two classes. We'll demonstrate this by creating a spam detector that classifies text as either spam or not spam.

For binary classification, we can extract a boolean value by setting `response_model=bool` and prompting the model to classify the text:



```python
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini", response_model=bool)
def classify_spam(text: str) -> str:
    return f"Classify the following text as spam or not spam: {text}"


text = "Would you like to buy some cheap viagra?"
label = classify_spam(text)
assert label is True  # This text is classified as spam

text = "Hi! It was great meeting you today. Let's stay in touch!"
label = classify_spam(text)
assert label is False  # This text is classified as not spam
```

## Multi-Class Classification: Sentiment Analysis

Multi-class classification extends the concept to scenarios where we need to categorize text into one of several classes. We'll demonstrate this with a sentiment analysis task.

First, we define an `Enum` to represent our sentiment labels:



```python
from enum import Enum


class Sentiment(Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
```

Then, we set `response_model=Sentiment` to analyze the sentiment of the given text:


```python
from mirascope.core import openai


@openai.call("gpt-4o-mini", response_model=Sentiment)
def classify_sentiment(text: str) -> str:
    return f"Classify the sentiment of the following text: {text}"


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

So far we've demonstrated using simple types like `bool` and `Enum` for classification, but we can extend this approach using Pydantic's `BaseModel` class to extract additional information beyond just the classification label.

For example, we can gain insight to the LLMs reasoning for the classified label simply by including a reasoning field in our response model and updating the prompt:



```python
from enum import Enum

from mirascope.core import openai
from pydantic import BaseModel


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
print(f"Sentiment: {response.sentiment}")
print(f"Reasoning: {response.reasoning}")
```

    Sentiment: Sentiment.NEUTRAL
    Reasoning: The text expresses a positive sentiment towards the product because the speaker is willing to recommend it. However, the mention of 'if it were cheaper' introduces a condition that makes the overall sentiment appear somewhat negative, as it suggests dissatisfaction with the current price. Therefore, the sentiment can be classified as neutral, as it acknowledges both a positive recommendation but also a negative aspect regarding pricing.


## Handling Uncertainty

When dealing with LLMs for classification tasks, it's important to account for cases where the model might be uncertain about its prediction. We can modify our approach to include a certainty score and handle cases where the model's confidence is below a certain threshold.



```python
from pydantic import BaseModel, Field


class SentimentAnalysisWithCertainty(BaseModel):
    sentiment: Sentiment
    certainty: float = Field(..., ge=0, le=1)
    reasoning: str


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
```

    The model is not certain enough about the classification.


<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Content Moderation</b>Classify user-generated content as appropriate, inappropriate, or requiring manual review</li>
<li><b>Customer Support Triage</b>Categorize incoming support tickets by urgency or department.</li>
<li><b>News Article Categorization</b>Classify news articles into topics (e.g. politics, sports, technology, etc)</li>
<li><b>Intent Recognition</b>Identify user intent in chatbot interactions (e.g. make a purchase, ask for help, etc.)</li>
<li><b>Email Classification</b>Sort emails into categories like personal, work-related, promotional, or urgent</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider the following:

- Refine your prompts to provide clear instructions and relevant context for your specific classification task.
- Experiment with different model providers and version to balance accuracy and speed.
- Implement error handling and fallback mechanisms for cases where the model's classification is uncertain.
- Consider using a combination of classifiers for more complex categorization tasks.

## Comparison with Traditional Machine Learning Models

Training text classification models requires a much more involved workflow:

- Preprocessing:
    - Read in data, clean and standardize it, and split it into training, validation, and test datasets
- Feature Extraction:
    - Basic: bag of words, TF-IDF
    - Advanced: word embeddings, contextual embeddings
- Classification Algorithm / Machine Learning Algorithm:
    - Basic: Naive Bayes, logistic regression, linear classifiers
    - Advanced: Neural networks, transformers (e.g. BERT)
- Model Training:
    - Train on training data and validate on validation data, adjusting batch size and epochs.
    - Things like activation layers and optimizers can greatly impact the quality of the final trained model
- Model Evaluation:
    - Evaluate model quality on the test dataset using metrics such as F1-score, recall, precision, accuracy — whichever metric best suits your use-case
    
Many frameworks such as TensorFlow and PyTorch make implementing such workflows easier, but it is still far more involved that the approach we showed in the beginning using Mirascope.

If you’re interested in taking a deeper dive into this more traditional approach, the [TensorFlow IMDB Text Classification](https://www.tensorflow.org/tutorials/keras/text_classification_with_hub) tutorial is a great place to start.



