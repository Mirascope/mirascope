# LLM Validation With Retries

This recipe demonstrates how to leverage Large Language Models (LLMs) -- specifically Anthropic's Claude 3.5 Sonnet -- to perform automated validation on any value. We'll cover how to use **LLMs for complex validation tasks**, how to integrate this with Pydantic's validation system, and how to leverage [Tenacity](https://tenacity.readthedocs.io/en/latest/) to automatically **reinsert validation errors** back into an LLM call to **improve results**.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Model](../learn/response_models.md)
    - [Tenacity Integration](../integrations/tenacity.md)

!!! note "Background"

    While traditional validation tools like type checkers or Pydantic are limited to hardcoded rules (such as variable types or arithmetic), LLMs allow for much more nuanced and complex validation. This approach can be particularly useful for validating natural language inputs or complex data structures where traditional rule-based validation falls short.

## Setup

To set up our environment, first let's install all of the packages we will use:

```shell
pip install "mirascope[anthropic,tenacity]"
```

Make sure to also set your `ANTHROPIC_API_KEY` if you haven't already.

## Basic LLM Validation

Let's start with a simple example of using an LLM to check for spelling and grammatical errors in a text snippet:

```python
--8<-- "examples/cookbook/llm_validation_with_retries/basic_validation.py"
```

## Pydantic's AfterValidator

We can use Pydantic's [`AfterValidator`](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.AfterValidator) to integrate our LLM-based validation directly into a Pydantic model:

```python
--8<-- "examples/cookbook/llm_validation_with_retries/after_validator.py:1:4"
--8<-- "examples/cookbook/llm_validation_with_retries/after_validator.py:26:52"
```

## Reinsert Validation Errors For Improved Performance

One powerful technique for enhancing LLM generations is to automatically reinsert validation errors into subsequent calls. This approach allows the LLM to learn from its previous mistakes as few-shot examples and improve it's output in real-time. We can achieve this using Mirascope's integration with Tenacity, which collects `ValidationError` messages for easy insertion into the prompt.

```python
--8<-- "examples/cookbook/llm_validation_with_retries/validation_errors_with_retries.py:1:12"
--8<-- "examples/cookbook/llm_validation_with_retries/validation_errors_with_retries.py:32:72"
```

!!! tip "Additional Real-World Examples"

    - Code Review: Validate code snippets for best practices and potential bugs.
    - Data Quality Checks: Validate complex data structures for consistency and completeness.
    - Legal Document Validation: Check legal documents for compliance with specific regulations.
    - Medical Record Validation: Ensure medical records are complete and consistent.
    - Financial Report Validation: Verify financial reports for accuracy and compliance with accounting standards.

When adapting this recipe to your specific use-case, consider the following:

- Tailor the prompts to provide clear instructions and relevant context for your specific validation tasks.
- Balance the trade-off between validation accuracy and performance, especially when implementing retries.
- Implement proper error handling and logging for production use.
- Consider caching validation results for frequently validated items to improve performance.
