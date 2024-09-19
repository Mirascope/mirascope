# Named Entity Recognition

This guide demonstrates techniques to perform Named Entity Recognition (NER) using Large Language Models (LLMs) with various levels of nested entity recognition. We'll use Groq's llama-3.1-8b-instant model, but you can adapt this approach to other models with similar capabilities.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Model](../learn/response_models.md)

## Background

Named Entity Recognition is a subtask of information extraction that seeks to locate and classify named entities in text into predefined categories such as person names, organizations, locations, etc. LLMs have revolutionized NER by enabling more context-aware and hierarchical entity recognition, going beyond traditional rule-based or statistical methods.

!!! note "LLMs Are Not Trained Specifically For NER"

    It's worth noting that there are models that are trained specifically for NER (such as GLiNER). These models are often much smaller and cheapr and can often get better results for the right tasks. LLMs should generally be reserved for quick and dirty prototyping for NER or for tasks that may require a more nuanced, open-ended language-based approach. For example, an NER system that accepts user input to guide the system by be easier to build using LLMs than a traditionally trained NER-specific model.

## Setup

First, ensure you have the necessary packages installed and API keys set:

```bash
pip install "mirascope[groq]"
```

Set your Groq API key as an environment variable:

```bash
export GROQ_API_KEY=your_api_key_here
```


## Simple NER

We'll implement NER with different levels of complexity: simple and nested entity recognition. Let's start with the simple version:

```python
--8<-- "examples/cookbook/named_entity_recognition.py::52"
```

In this example, we're extracting entities that have just the entity's text and label. However, entities often have relationships that are worth extracting and understanding.

## Nested NER

Now, let's implement a more sophisticated version that can handle nested entities:

```python
--8<-- "examples/cookbook/named_entity_recognition.py:55:139"
```

## Testing

To ensure robustness, it's crucial to test the NER system with diverse scenarios. Here's a function to run multiple test cases:

```python
--8<-- "examples/cookbook/named_entity_recognition.py:141:248"
```

It's important to heavily test any system before you put it in practice. The above example demonstrates how to test such a method (`nested_ner` in this case), but it only shows a single input/output pair for brevity.

We strongly encourage you to write far more robust tests in your applications with many more test cases. This is why our examples uses `@pytest.mark.parametrize` to easily include additional test cases.

## Further Improvements

This Named Entity Recognition (NER) system leverages the power of LLMs to perform context-aware, hierarchical entity extraction with various levels of nesting. It can identify complex relationships between entities, making it suitable for a wide range of applications.

!!! tip "Additional Real-World Applications"

    - **Information Extraction**: Extracting structured information from unstructured text data.
    - **Question Answering**: Identifying entities relevant to a given question.
    - **Document Summarization**: Summarizing documents by extracting key entities and relationships.
    - **Sentiment Analysis**: Analyzing sentiment towards specific entities or topics.

When adapting this recipe to your specific use-case, consider the following:

- Prompt customization to guide the model towards specific entity types or relationships.
- Fine-tuning the model on domain-specific data for better accuracy in particular fields.
- Implementing a confidence score for each identified entity.
- Integrating with a knowledge base to enhance entity disambiguation.
- Developing a post-processing step to refine and validate the LLM's output.
- Exploring ways to optimize performance for real-time applications.

By leveraging the power of LLMs and the flexibility of the Mirascope library, you can create sophisticated NER systems that go beyond traditional approaches, enabling more nuanced and context-aware entity recognition for various applications.
