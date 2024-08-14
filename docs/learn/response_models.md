# Response Models

Response Models in Mirascope provide a powerful way to structure and validate the output from Large Language Models (LLMs). By leveraging Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/usage/models/), Response Models offer type safety, automatic validation, and easier data manipulation for your LLM responses. While we cover some details in this documentation, we highly recommend reading through Pydantic's documentation for a deeper, comprehensive dive into everything you can do with Pydantic and `BaseModel`s.

## Why Use Response Models?

1. **Structured Output**: Define exactly what you expect from the LLM, ensuring consistency in responses.
2. **Automatic Validation**: Pydantic handles type checking and validation, reducing errors in your application.
3. **Improved Type Hinting**: Better IDE support and clearer code structure.
4. **Easier Data Manipulation**: Work with Python objects instead of raw strings or dictionaries.

## Using Response Models

To use a Response Model, define a Pydantic model and pass it to the `response_model` parameter in the `call` decorator:

```python
from mirascope.core import openai, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


book = recommend_book("science fiction")
assert isinstance(book, Book)
print(f"Title: {response.title}")
print(f"Author: {response.author}")
```

This approach works consistently across all supported providers in Mirascope.

## JSON Mode and Response Models

When using Response Models, the default setting is `json_mode=False`, which will use [`Tools`](./tools.md) under the hood to perform the structured output extraction. However, for some providers setting `json_mode=True` enables support for field types that may not be supported by tools.

!!! note "Not All Providers Have Explicit JSON Mode Support"

    In cases where a model provider does not have explicit JSON Mode support, Mirascope implements a pseudo JSON Mode by instructing the model to output JSON in the prompt. Since all providers support [`Tools`](./tools.md), the default when using `response_model` is `json_mode=False`.

We generally recommend testing both settings to see which works better for your use-case. For more details on JSON Mode, refer to the [JSON Mode documentation](./json_mode.md).

### Field Type Support Across Providers

The support for different field types varies across providers. Here's a comprehensive overview:

|     Type      | Anthropic | Cohere | Gemini | Groq | Mistral | OpenAI |
|---------------|-----------|--------|--------|------|---------|--------|
|     str       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     int       |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|    float      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bool      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     bytes     |✓✓|✓✓|-✓|✓✓|✓✓|✓✓|
|     list      |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|     set       |✓✓|✓✓|--|✓✓|✓✓|✓✓|
|     tuple     |✓✓|✓✓|-✓|✓✓|✓✓|-✓|
|     dict      |✓✓|✓✓|✓✓|✓✓|✓✓|-✓|
|  Literal/Enum |✓✓|✓✓|✓✓|✓✓|✓✓|✓✓|
|   BaseModel   |✓✓|-✓|✓✓|✓✓|✓✓|✓✓|
| Nested ($def) |✓✓|--|--|✓✓|✓✓|✓✓|

✓✓ : Fully Supported, -✓: Only JSON Mode Support, -- : Not supported

## Error Handling and Validation

While Response Models significantly improve output structure and validation, it's important to handle potential errors:

```python
from pydantic import ValidationError

try:
    response = recommend_book("science fiction")
    print(response.title)
except ValidationError as e:
    print(f"Validation error: {e}")
```

For robust applications, consider implementing retry logic with validation error feedback. Mirascope's integration with Tenacity makes this process straightforward. Check out the [Tenacity integration documentation](../integrations/tenacity.md) to learn how to easily reinsert validation errors into subsequent retry calls, improving performance and reliability.

## Best Practices

- **Use Clear Field Names**: Choose descriptive names for your model fields to guide the LLM's output.
- **Provide Field Descriptions**: Use Pydantic's `Field` with descriptions to give the LLM more context.
- **Start Simple**: Begin with basic types and gradually increase complexity as needed.
- **Handle Errors Gracefully**: Implement proper error handling and consider using retry mechanisms.
- **Leverage JSON Mode**: When possible, use `json_mode=True` for better type support and consistency.
- **Test Thoroughly**: Validate your Response Models across different inputs and edge cases.

By leveraging Response Models effectively, you can create more robust, type-safe, and maintainable LLM-powered applications with Mirascope.