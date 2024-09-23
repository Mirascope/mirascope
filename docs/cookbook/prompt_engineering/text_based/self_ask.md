# Self-Ask: Enhancing LLM Reasoning with Follow-Up Questions

This recipe demonstrates how to implement the Self-Ask technique using Large Language Models (LLMs) with Mirascope. Self-Ask is a prompt engineering method that enhances an LLM's reasoning capabilities by encouraging it to ask and answer follow-up questions before providing a final answer. We'll explore both a basic implementation and an enhanced version with dynamic example selection.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../../learn/prompts.md)
    - [Calls](../../../learn/calls.md)

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
--8<-- "examples/cookbook/prompt_engineering/text_based/self_ask/self_ask.py:1:45"
    # ... (add more examples here)
--8<-- "examples/cookbook/prompt_engineering/text_based/self_ask/self_ask.py:98:108"
```

This basic implementation demonstrates how to use few-shot learning with Self-Ask. The `self_ask` function takes a query and a list of examples, then uses Mirascope's `OpenAIDynamicConfig` to inject the examples into the prompt.

## Enhanced Self-Ask with Dynamic Example Selection

Now, let's improve our implementation by adding dynamic example selection:

```python
--8<-- "examples/cookbook/prompt_engineering/text_based/self_ask/enhanced_self_ask.py:1:50"
# Use the enhanced Self-Ask implementation
--8<-- "examples/cookbook/prompt_engineering/text_based/self_ask/enhanced_self_ask.py:122:131"

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
