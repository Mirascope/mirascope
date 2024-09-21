# Text Classification with Large Language Models

In this recipe we’ll explore using Mirascope to implement binary classification, multi-class classification, and various other extensions of these classification techniques — specifically using Python the OpenAI API. We will also compare these solutions with more traditional machine learning and Natural Language Processing (NLP) techniques.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Models](../learn/response_models.md)

!!! note "Background"

    Text classification is a fundamental classification problem and NLP task that involves categorizing text documents into predefined classes or categories. Historically this has required training text classifiers through more traditional machine learning methods. Large Language Models (LLMs) have revolutionized this field, making sophisticated classification tasks accessible through simple API calls and thoughtful prompt engineering.

## Key Concepts in Text Classification

Before getting started, let’s cover some essential concepts in text classification:

- **Binary Classification**: Categorizing text into one of two classes (e.g., spam or not spam)
- **Multi-Class Classification**: Categorizing text into one of several classes (e.g., sentiment analysis)
- **Large Language Models (LLMs)**: Advanced AI models trained on large datasets that are capable of ingesting text data and generating text data outputs, which we will access through provider API endpoints
- **Natural Language Processing (NLP)**: A field of artificial intelligence focused on the interaction between computers and human language
- **Deep Learning**: A machine learning subset focused on enabling systems to learn and improve from training datasets without explicit programming of behavior

Text classification has become an indispensable tool, with applications spanning various industries and use cases, such as spam detection, sentiment analysis, content categorization, social media monitoring, medical text classification, and many more.

## Setting Up Your Environment

To set up our environment, first let's install all of the packages we will use:

```shell
pip install "mirascope[openai]"
```

Make sure to also set your `OPENAI_API_KEY` if you haven't already.

## Binary Classification: Spam Detection

Binary classification involves categorizing text into one of two classes. We'll demonstrate this by creating a spam detector that classifies text as either spam or not spam.

For binary classification, we can extract a boolean value by setting `response_model=bool` and prompting the model to classify the text:

```python
--8<-- "examples/cookbook/text_classification/binary_classification.py"
```

## Multi-Class Classification: Sentiment Analysis

Multi-class classification extends the concept to scenarios where we need to categorize text into one of several classes. We'll demonstrate this with a sentiment analysis task.

First, we define an `Enum` to represent our sentiment labels:

```python
--8<-- "examples/cookbook/text_classification/multiclass_classification.py:1:2"
--8<-- "examples/cookbook/text_classification/multiclass_classification.py:5:9"
```

Then, we set `response_model=Sentiment` to analyze the sentiment of the given text:

```python
--8<-- "examples/cookbook/text_classification/multiclass_classification.py"
```

## Classification with Reasoning

So far we've demonstrated using simple types like `bool` and `Enum` for classification, but we can extend this approach using Pydantic's `BaseModel` class to extract additional information beyond just the classification label.

For example, we can gain insight to the LLMs reasoning for the classified label simply by including a reasoning field in our response model and updating the prompt:

```python
--8<-- "examples/cookbook/text_classification/classification_with_reasoning.py"
```

## Handling Uncertainty

When dealing with LLMs for classification tasks, it's important to account for cases where the model might be uncertain about its prediction. We can modify our approach to include a certainty score and handle cases where the model's confidence is below a certain threshold.

```python
--8<-- "examples/cookbook/text_classification/handle_uncertainty.py:3:7"
--8<-- "examples/cookbook/text_classification/handle_uncertainty.py:14:39"
```

!!! tip "Additional Real-World Examples"

    - **Content Moderation**: Classify user-generated content as appropriate, inappropriate, or requiring manual review.
    - **Customer Support Triage**: Categorize incoming support tickets by urgency or department.
    - **News Article Categorization**: Classify news articles into topics (e.g. politics, sports, technology, etc).
    - **Intent Recognition**: Identify user intent in chatbot interactions (e.g. make a purchase, ask for help, etc.).
    - **Email Classification**: Sort emails into categories like personal, work-related, promotional, or urgent.

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
