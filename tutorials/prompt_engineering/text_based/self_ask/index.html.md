# Self-Ask

This recipe demonstrates how to implement the Self-Ask technique using Large Language Models (LLMs) with Mirascope. Self-Ask is a prompt engineering method that enhances an LLM's reasoning capabilities by encouraging it to ask and answer follow-up questions before providing a final answer. We'll explore both a basic implementation and an enhanced version with dynamic example selection.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Automated Code Generation</b>: Generating boilerplate or units tests for more productivity.</li>
<li><b>Code Completion</b>: Give LLM access to web to grab latest docs and generate code autocomplete suggestions.</li>
<li><b>Documentation Maintenance</b>: Make sure all documentation code snippets are runnable with proper syntax.</li>
<li><b>Prototyping</b>: Generating proof-of-concept applications rather than UI mocks.</li>
</ul>
</div>

## Setup

To set up our environment, first let's install all of the packages we will use:


```python
!pip install "mirascope[openai]" numpy scikit-learn
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```


## Basic Self-Ask Implementation

Let's start with a basic implementation of Self-Ask using few-shot learning examples:


```python
import inspect

from mirascope.core import openai, prompt_template
from typing_extensions import TypedDict


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

query = "The birth country of Jayantha Ketagoda left the British Empire when?"
response = self_ask(query=query, examples=few_shot_examples)
print(response.content)

response = self_ask(query=query, examples=[])
print(response.content)
```

    Are follow up questions needed here: Yes.  
    Follow up: Which country is Jayantha Ketagoda from?  
    Intermediate answer: Jayantha Ketagoda is from Sri Lanka.  
    Follow up: When did Sri Lanka leave the British Empire?  
    Intermediate answer: Sri Lanka gained independence from the British Empire on February 4, 1948.  
    So the final answer is: February 4, 1948.
    Jayantha Ketagoda was born in Sri Lanka, which was formerly known as Ceylon. Sri Lanka gained independence from the British Empire on February 4, 1948.



This basic implementation demonstrates how to use few-shot learning with Self-Ask. The `self_ask` function takes a query and a list of examples, then uses Mirascope's `OpenAIDynamicConfig` to inject the examples into the prompt.

## Enhanced Self-Ask with Dynamic Example Selection

Now, let's improve our implementation by adding dynamic example selection:



```python
import inspect

import numpy as np
from mirascope.core import openai, prompt_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing_extensions import TypedDict


class FewShotExample(TypedDict):
    question: str
    answer: str


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


query = "What was the primary language spoken by the inventor of the phonograph?"
response = dynamic_self_ask(query=query, examples=few_shot_examples, n=2)
print(response.content)
```

    Are follow up questions needed here: Yes.  
    Follow up: Who invented the phonograph?  
    Intermediate answer: Thomas Edison.  
    Follow up: What language did Thomas Edison primarily speak?  
    Intermediate answer: Thomas Edison primarily spoke English.  
    So the final answer is: English.



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

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Complex Problem Solving</b>: Use Self-Ask for multi-step problems in fields like mathematics or engineering.</li>
<li><b>Research Assistance</b>: Implement Self-Ask to help researchers explore complex topics and formulate hypotheses.</li>
<li><b>Legal Analysis</b>: Apply Self-Ask to break down complex legal questions and explore relevant precedents.</li>
<li><b>Medical Diagnosis</b>: Use Self-Ask to guide through differential diagnosis processes.</li>
<li><b>Customer Support</b>: Implement Self-Ask to handle complex customer queries that require multiple pieces of information.</li>
</ul>
</div>


When adapting this recipe to your specific use-case, consider:

- Tailoring the few-shot examples to your domain for better performance.
- Experimenting with different prompts and example formats to optimize the Self-Ask process.
- Implementing a feedback loop to continuously improve the quality of the Self-Ask responses.
- Combining Self-Ask with other techniques like chain-of-thought for even more powerful reasoning capabilities.

By leveraging Mirascope's `call` decorator and `prompt_template`, you can easily implement and customize the Self-Ask technique to enhance your LLM's reasoning capabilities across a wide range of applications.

