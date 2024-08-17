# Self-Ask: Enhancing LLM Reasoning with Follow-Up Questions

This recipe demonstrates how to implement the Self-Ask technique using Large Language Models (LLMs) with Mirascope. Self-Ask is a prompt engineering method that enhances an LLM's reasoning capabilities by encouraging it to ask and answer follow-up questions before providing a final answer. We'll explore both a basic implementation and an enhanced version with dynamic example selection.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../../learn/prompts.md)
    - [Calls](../../../learn/calls.md)
    - [Dynamic Configuration](../../../learn/dynamic_configuration.md)

!!! note "Background"

    [Self-Ask](https://arxiv.org/pdf/2210.03350) is a prompt engineering technique introduced in 2022. It outperforms other methods like chain-of-thought reasoning across multiple benchmarks. The technique involves prompting the LLM to consider whether follow-up questions are needed, then answer those questions before arriving at a final answer. This approach can significantly improve the accuracy and depth of the LLM's responses, especially for complex queries.

## Setup

To set up our environment, first let's install all of the packages we will use:

```shell
pip install "mirascope[openai]" numpy scikit-learn
```

Make sure to also set your `OPENAI_API_KEY` if you haven't already.

## Basic Self-Ask Implementation

Let's start with a basic implementation of Self-Ask using few-shot learning examples:

```python
import inspect
from typing_extensions import TypedDict

from mirascope.core import openai, prompt_template

class FewShotExample(TypedDict):
    question: str
    answer: str

@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Examples:
    {examples:lists}

    Query: {query}
    """
)
def self_ask(query: str, examples: list[FewShotExample]) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "examples": [
                [example["question"], example["answer"]] for example in examples
            ]
        }
    }

# Define few-shot examples
few_shot_examples = [
    FewShotExample(
        question="When does monsoon season end in the state the area code 575 is located?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Which state is the area code 575 located in?
            Intermediate answer: The area code 575 is located in New Mexico.
            Follow up: When does monsoon season end in New Mexico?
            Intermediate answer: Monsoon season in New Mexico typically ends in mid-September.
            So the final answer is: mid-September.
            """
        ),
    ),
    # ... (add more examples here)
]

query = "The birth country of Jayantha Ketagoda left the British Empire when?"
response = self_ask(query=query, examples=few_shot_examples)
print(response.content)
# > Are follow up questions needed here: Yes.
#   Follow up: What is the birth country of Jayantha Ketagoda?
#   Intermediate answer: Jayantha Ketagoda is from Sri Lanka.
#   Follow up: When did Sri Lanka leave the British Empire?
#   Intermediate answer: Sri Lanka, formerly known as Ceylon, gained independence from the British Empire on February 4, 1948.
#   So the final answer is: February 4, 1948.
```

This basic implementation demonstrates how to use few-shot learning with Self-Ask. The `self_ask` function takes a query and a list of examples, then uses Mirascope's `OpenAIDynamicConfig` to inject the examples into the prompt.

## Enhanced Self-Ask with Dynamic Example Selection

Now, let's improve our implementation by adding dynamic example selection:

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def select_relevant_examples(
    query: str, examples: list[FewShotExample], n: int = 3
) -> list[FewShotExample]:
    """Select the most relevant examples based on cosine similarity."""
    vectorizer = TfidfVectorizer().fit([ex["question"] for ex in examples] + [query])
    example_vectors = vectorizer.transform([ex["question"] for ex in examples])
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(query_vector, example_vectors)[0]
    most_similar_indices = np.argsort(similarities)[-n:][::-1]

    return [examples[i] for i in most_similar_indices]

@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Examples:
    {examples:lists}

    Query: {query}
    """
)
def dynamic_self_ask(
    query: str, examples: list[FewShotExample], n: int = 3
) -> openai.OpenAIDynamicConfig:
    relevant_examples = select_relevant_examples(query, examples, n)
    return {
        "computed_fields": {
            "examples": [
                [example["question"], example["answer"]]
                for example in relevant_examples
            ]
        }
    }

# Use the enhanced Self-Ask implementation
query = "What was the primary language spoken by the inventor of the phonograph?"
response = dynamic_self_ask(query=query, examples=few_shot_examples, n=2)
print(response.content)
# > Are follow up questions needed here: Yes.
#   Follow up: Who invented the phonograph?
#   Intermediate answer: Thomas Edison.
#   Follow up: What language did Thomas Edison primarily speak?
#   Intermediate answer: Thomas Edison primarily spoke English.
#   So the final answer is: English.
```

This enhanced version introduces the `select_relevant_examples` function, which uses TF-IDF vectorization and cosine similarity to find the most relevant examples for a given query. The `dynamic_self_ask` function then selects these relevant examples before including them in the prompt.

## Benefits and Considerations

The enhanced Self-Ask implementation offers several advantages:

1. Reduced prompt size by including only the most relevant examples.
2. Potentially improved response quality by focusing on the most applicable few-shot examples.
3. Ability to maintain a larger pool of examples without always including all of them in every query.

When implementing this technique, consider:

- Balancing the number of selected examples with the desired prompt length and model context window.
- Experimenting with different similarity metrics or embedding techniques for example selection.
- Regularly updating your example pool to cover a wide range of query types and topics.

!!! tip "Additional Real-World Applications"

    - Complex Problem Solving: Use Self-Ask for multi-step problems in fields like mathematics or engineering.
    - Research Assistance: Implement Self-Ask to help researchers explore complex topics and formulate hypotheses.
    - Legal Analysis: Apply Self-Ask to break down complex legal questions and explore relevant precedents.
    - Medical Diagnosis: Use Self-Ask to guide through differential diagnosis processes.
    - Customer Support: Implement Self-Ask to handle complex customer queries that require multiple pieces of information.

When adapting this recipe to your specific use-case, consider:

- Tailoring the few-shot examples to your domain for better performance.
- Experimenting with different prompts and example formats to optimize the Self-Ask process.
- Implementing a feedback loop to continuously improve the quality of the Self-Ask responses.
- Combining Self-Ask with other techniques like chain-of-thought for even more powerful reasoning capabilities.

By leveraging Mirascope's `call` decorator and `prompt_template`, you can easily implement and customize the Self-Ask technique to enhance your LLM's reasoning capabilities across a wide range of applications.
