# Chaining

Chaining in Mirascope allows you to combine multiple LLM calls or operations in a sequence to solve complex tasks. Mirascope's approach to chaining leverages dynamic configuration and computed fields, providing a unique and powerful way to create sophisticated LLM-powered applications.

## Chaining with Dynamic Configuration

The primary method of chaining in Mirascope involves using dynamic configuration with computed fields. This approach allows you to pass the results of previous steps as inputs to subsequent steps in the chain.

### How It Works

1. Each step in the chain is defined as a separate function decorated with a Mirascope LLM call decorator (e.g., `@openai.call`).
2. The functions return a dynamic configuration dictionary that includes `computed_fields`.
3. These `computed_fields` can contain the results of previous steps, allowing you to pass information through the chain.

### Example

Here's a basic example of chaining using dynamic configuration:

```python
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Summarize this text: {text}")
def summarize(text: str):
    ...


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Translate this text to {language}: {summary}")
def summarize_and_translate(text: str, language: str) -> openai.OpenAIDynamicConfig:
    return {"computed_fields": {"summary": summarize(text)}}


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
print(response.model_dump()["computed_fields"])  # This will contain the `summarize` response
```

In this example, the `summarize_and_translate` function uses a computed field to pass the summary from the previous step.

## Benefits of Chaining with Computed Fields

- **Traceability**: By using computed fields, each step's inputs and outputs are recorded in the final `model_dump()`, providing a clear trace of the entire chain's execution.
- **Flexibility**: You can easily modify or extend the chain by adding or changing computed fields.
- **Debugging**: The `model_dump()` method provides a comprehensive view of the chain's execution, making it easier to debug complex chains.

## Chaining Without Computed Fields

While using computed fields is the recommended approach in Mirascope, you can also chain calls without them:

```python
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Translate this text to {language}: {summary}")
def translate(summary: str, language: str): ...


def summarize_and_translate(original_text: str):
    summary = summarize(original_text)
    translation = translate(summary.content, "french")
    return translation.content
```

### Pros and Cons

Pros of not using computed fields:

- Slightly simpler code for very basic chains
- More familiar to those used to traditional function chaining

Cons of not using computed fields:

- Less traceable
- Harder to debug complex chains
- Doesn't take full advantage of Mirascope's features

## Advanced Chaining Techniques

Check out our [cookbook recipes on chaining](../cookbook/prompt_engineering/chaining_based/index.md) to see examples of more advanced chaining techniques.

## Best Practices

- **Use Computed Fields**: Leverage computed fields for better traceability and debugging.
- **Modular Design**: Break down complex tasks into smaller, reusable functions.
- **Error Handling**: Implement robust error handling at each step of your chain.
- **Use Response Models**: Structure your intermediate outputs for better type safety and easier processing. Check out the [`Response Models`](./response_models.md) documentation for more details.
- **Asynchronous Operations**: Utilize async programming for parallel processing when appropriate. Check out the [`Async`](./async.md) documentation for more details.
- **Testing**: Test each component of your chain individually as well as the entire chain.
- **Logging**: Use the `model_dump()` method to log the entire chain's execution for debugging and analysis. This pairs well with [custom middleware](../integrations/middleware.md).

By mastering Mirascope's chaining techniques, you can create sophisticated LLM-powered applications that tackle complex, multi-step problems with greater accuracy, control, and traceability.
