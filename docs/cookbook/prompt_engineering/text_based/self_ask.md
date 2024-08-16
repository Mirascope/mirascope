# Self-Ask: Enhancing LLM Reasoning with Follow-Up Questions

This recipe demonstrates how to implement the Self-Ask technique using Large Language Models (LLMs). Self-Ask is a prompt engineering method that enhances an LLM's reasoning capabilities by encouraging it to ask and answer follow-up questions before providing a final answer. Mirascope makes the implementation simple, reusable, and extensible.

??? info "Key Concepts"

    - [Prompts](../../../learn/prompts.md)
    - [Calls](../../../learn/calls.md)
    - [Response Model](../../../learn/response_models.md)

!!! note "Background"

    [Self-Ask](https://arxiv.org/pdf/2210.03350) is a prompt engineering technique introduced in 2022. It outperforms other methods like chain-of-thought reasoning across multiple benchmarks. The technique involves prompting the LLM to consider whether follow-up questions are needed, then answer those questions before arriving at a final answer. This approach can significantly improve the accuracy and depth of the LLM's responses, especially for complex queries.

## Setup

To set up our environment, first let's install all of the packages we will use:

```shell
pip install "mirascope[openai]" numpy scikit-learn
```

Make sure to also set your `OPENAI_API_KEY` if you haven't already.

## Implementing Self-Ask with Few-Shot Learning

!!! note ""

    [self_ask.py](ADD LINK)

To implement Self-Ask, we'll use few-shot learning examples that demonstrate the technique, taking advantage of Mirascope's `lists` format spec convenience to inject the examples into the LLM call's prompt.

First, let's define a structure for our few-shot examples:

```python
from typing_extensions import TypedDict


class FewShotExample(TypedDict):
    question: str
    answer: str
```

Next, we'll create an LLM call function that can incorporate `FewShotExample` instances:

```python
from mirascope.core import openai, prompt_template


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
```

Now, let's define our few-shot examples:

```python
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
    FewShotExample(
        question="What is the current official currency in the country where Ineabelle Diaz is a citizen?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Which country is Ineabelle Diaz a citizen of?
            Intermediate answer: Ineabelle Diaz is from Peurto Rico, which is in the United States of America.
            Follow up: What is the current official currency in the United States of America?
            Intermediate answer: The current official currency in the United States is the United States dollar.
            So the final answer is: United States dollar.
            """
        ),
    ),
    FewShotExample(
        question="Where was the person who founded the American Institute of Public Opinion in 1935 born?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Who founded the American Institute of Public Opinion in 1935?
            Intermediate answer: George Gallup.
            Follow up: Where was George Gallup born?
            Intermediate answer: George Gallup was born in Jefferson, Iowa.
            So the final answer is: Jefferson.
            """
        ),
    ),
    FewShotExample(
        question="What language is used by the director of Tiffany Memorandum?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Who directed the movie called Tiffany Memorandum?
            Intermediate answer: Sergio Grieco.
            Follow up: What language is used by Sergio Grieco?
            Intermediate answer: Sergio Grieco speaks Italian.
            So the final answer is: Italian.
            """
        ),
    ),
    FewShotExample(
        question="What is the sports team the person played for who scored the first touchdown in Superbowl 1?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Which player scored the first touchdown in Superbowl 1?
            Intermediate answer: Max McGee.
            Follow up: Which sports team did Max McGee play for?
            Intermediate answer: Max McGee played for the Green Bay Packers.
            So the final answer is: Green Bay Packers.
            """
        ),
    ),
]
```

Finally, we can use our Self-Ask implementation:

```python
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

Let's compare this to asking the same question with no few-shot examples:

```python
response = self_ask(query=query, examples=[])
print(response.content)
# > Jayantha Ketagoda was born in Sri Lanka, which was known as Ceylon during the
#   British colonial period. Ceylon gained independence from the British Empire on
#   February 4, 1948.
```

## Enhancing Self-Ask Implementation

!!! note ""

    [enhanced_self_ask.py](ADD LINK)

To further improve our Self-Ask implementation, consider the following enhancements:

- Dynamic example selection: Choose relevant few-shot examples based on the input query.
- Fallback mechanism: Implement a fallback to standard querying if Self-Ask doesn't improve the result.
- Result validation: Add a step to validate the final answer against the initial query.

Here's an example of how you might implement dynamic example selection:

```python
from mirascope.core import openai, prompt_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


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

In this enhanced version we define a `select_relevant_examples` function that uses TF-IDF vectorization and cosine similarity to find the most relevant examples for a given query.
The `dynamic_self_ask` function now selects relevant examples before including them in the prompt.

This approach has several benefits:

- It reduces the prompt size by only including the most relevant examples.
- It potentially improves the quality of the response by focusing on the most applicable few-shot examples.
- It allows for a larger pool of examples to be maintained without always including all of them in every query.

When implementing this enhancement, consider:

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
