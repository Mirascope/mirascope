# Calls

??? api "API Documentation"

    [`mirascope.core.anthropic.call`](../api/core/anthropic/call.md)

    [`mirascope.core.azure.call`](../api/core/azure/call.md)

    [`mirascope.core.cohere.call`](../api/core/cohere/call.md)

    [`mirascope.core.gemini.call`](../api/core/gemini/call.md)

    [`mirascope.core.groq.call`](../api/core/groq/call.md)

    [`mirascope.core.litellm.call`](../api/core/litellm/call.md)

    [`mirascope.core.mistral.call`](../api/core/mistral/call.md)

    [`mirascope.core.openai.call`](../api/core/openai/call.md)

    [`mirascope.core.vertex.call`](../api/core/vertex/call.md)

The `call` decorator is a core feature of the Mirascope library, designed to simplify and streamline interactions with various Large Language Model (LLM) providers. This powerful tool allows you to transform Python functions into LLM API calls with minimal boilerplate code while providing type safety and consistency across different providers.

## Purpose and Benefits

The primary purposes and benefits of the `call` decorator are to:

- Reduce the learning curve necessary to use various different LLM providers
- Provide a unified interface for making LLM calls that abstracts away the various differences between provider APIs
- Enable easy switching between different LLM providers
- Enhance code readability and maintainability

By using the `call` decorator, you can focus on engineering your prompts and handling the LLM responses, rather than dealing with the intricacies of each provider's API.

## Basic Usage and Syntax

The basic syntax for using the `call` decorator is straightforward:

```python hl_lines="4"
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...

response = recommend_book("fantasy")
print(response.content)
```

In this example:

- The [`@prompt_template`](./prompts.md#prompt-templates) decorator turns the function into a prompt template.
- The `@openai.call` decorator transforms the prompt template into an LLM API call.
- We're using OpenAI's `gpt-4o-mini` model to make the call.
- When we call the function with `genre="fantasy"`, the argument is automatically injected into the prompt template and used in the call.

!!! info "Function Body"

    In the above example, we've used an ellipsis (`...`) for the function body, which returns `None`. If you'd like, you can always explicitly `return None` to be extra clear. The function body is used for dynamic configuration, which we'll cover in the [Call Parameters](#provider-specific-parameters) section.

## Supported Providers

Mirascope's `call` decorator supports multiple LLM providers, allowing you to easily switch between different models or compare outputs. Each provider has its own module within the Mirascope library. We currently support the following providers:

- [OpenAI](https://openai.com/) (and any provider with an OpenAI compatible endpoint)
- [Anthropic](https://www.anthropic.com/)
- [Mistral](https://mistral.ai/)
- [Gemini](https://gemini.google.com)
- [Groq](https://groq.com/)
- [Cohere](https://cohere.com/)
- [LiteLLM](https://www.litellm.ai/) (for multi-provider support)
- [Azure AI](https://azure.microsoft.com/en-us/solutions/ai)
- [Vertex AI](https://cloud.google.com/vertex-ai)

To use a specific provider, simply use the `call` decorator from the corresponding provider's module. Here's an example of how to use multiple different providers with the same prompt template:

```python hl_lines="9 12 15"
from mirascope.core import anthropic, mistral, openai, prompt_template


@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


openai_recommendation = openai.call("gpt-4o-mini")(recommend_book)("fantasy")
print("OpenAI recommendation:", openai_recommendation.content)

anthropic_recommendation = anthropic.call("claude-3-5-sonnet-20240620")(recommend_book)("fantasy")
print("Anthropic recommendation:", anthropic_recommendation.content)

mistral_recommendation = mistral.call("mistral-large-latest")(recommend_book)("fantasy")
print("Mistral recommendation:", mistral_recommendation.content)
```

This flexibility allows you to compare outputs from different providers or switch between them based on your specific needs without changing your core logic.

!!! note "Import Structure"

    We've shown importing each provider's module and using their respective `call` decorators. If preferred, you can instead directly import the non-aliased decorator (e.g. `from mirascope.core.openai import openai_call`).

## Common Parameters Across Providers

While each LLM provider has its own specific parameters, there are several common parameters that you'll find across all providers when using the `call` decorator. These parameters allow you to control various aspects of the LLM call:

- `model`: The only required parameter for all providers, which may be passed in as a standard argument (whereas all others are optional and must be provided as keyword arguments). It specifies which language model to use for the generation. Each provider has its own set of available models.
- `stream`: A boolean that determines whether the response should be streamed or returned as a complete response. We cover this in more detail in the [`Streams`](./streams.md) documentation.
- `tools`: A list of tools that the model may request to use in its response. We cover this in more detail in the [`Tools`](./tools.md) documentation.
- `response_model`: A Pydantic `BaseModel` type that defines how to structure the response. We cover this in more detail in the [`Response Models`](./response_models.md) documentation.
- `output_parser`: A function for parsing the response output. We cover this in more detail in the [`Output Parsers`](./output_parsers.md) documentation.
- `json_mode`: A boolean that deterines whether to use JSON mode or not. We cover this in more detail in the [`JSON Mode`](./json_mode.md) documentation.
- `client`: A custom client to use when making the call to the LLM. We cover this in more detail in the [`Custom Client`](./calls.md#custom-client) section below.
- `call_params`: The provider-specific parameters to use when making the call to that provider's API. We cover this in more detail in the [`Provider-Specific Parameters`](./calls.md#provider-specific-parameters) section below.

These common parameters provide a consistent way to control the behavior of LLM calls across different providers. Keep in mind that while these parameters are widely supported, there might be slight variations in how they're implemented or their exact effects across different providers (and the documentation should cover any such differences).

## Provider-Specific Parameters

??? api "API Documentation"

    [`mirascope.core.anthropic.call_params`](../api/core/anthropic/call_params.md)

    [`mirascope.core.cohere.call_params`](../api/core/cohere/call_params.md)

    [`mirascope.core.gemini.call_params`](../api/core/gemini/call_params.md)

    [`mirascope.core.groq.call_params`](../api/core/groq/call_params.md)

    [`mirascope.core.mistral.call_params`](../api/core/mistral/call_params.md)

    [`mirascope.core.openai.call_params`](../api/core/openai/call_params.md)

While Mirascope provides a consistent interface across different LLM providers, each provider has its own set of specific parameters that can be used to further configure the behavior of the model. These parameters are passed to the `call` decorator through the `call_params` argument.

For all providers, we have only included additional call parameters that are not already covered as shared arguments to the `call` decorator (e.g. `model`). We have also opted to exclude currently deprecated parameters entirely. However, since `call_params` is just a `TypedDict`, you can always include any additional keys at the expense of type errors (and potentially unknown behavior).

Here is an example using custom OpenAI call parameters to change the temperature:

```python hl_lines="4"
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini", call_params={"temperature": 0.7})
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


response = recommend_book("fantasy")
print(response.content)
```

In this example, we're setting the `temperature` parameter to 0.7, which affects the randomness of the model's output. A higher temperature (closer to 1.0) will result in more diverse and creative outputs, while a lower temperature (closer to 0.0) will make the outputs more focused and deterministic.

### Dynamic Configuration

You can also dynamically configure call parameters based on the function's input or other runtime conditions. This is done by returning a dictionary from the function body. Here's an example:

```python hl_lines="6 8-11"
from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    temperature = 0.9 if genre == "fantasy" else 0.5
    return {
        "call_params": {"temperature": temperature},
        "metadata": {"genre": genre}
    }


response = recommend_book("fantasy")
print(response.content)
print(f"Temperature used: {response.call_kwargs['temperature']}")
print(f"Metadata: {response.metadata}")
```

In this example, we're dynamically setting the `temperature` based on the genre, and also adding metadata to the call. The `OpenAIDynamicConfig` (or the equivalent for other providers) allows you to specify various dynamic configurations, including `call_params`, `metadata`, `computed_fields`, and more.

This approach allows for flexible, context-dependent configuration of your LLM calls.

## Custom Client

Mirascope allows you to use custom clients when making calls to LLM providers. This feature is particularly useful when you need to use specific client configurations, handle authentication in a custom way, or work with self-hosted models.

To use a custom client, you can pass it to the `call` decorator using the `client` parameter. Here's an example using a custom OpenAI client:

```python hl_lines="5-9 12"
from openai import OpenAI
from mirascope.core import openai, prompt_template

# Create a custom OpenAI client
custom_client = OpenAI(
    api_key="your-api-key",
    organization="your-organization-id",
    base_url="https://your-custom-endpoint.com/v1"
)


@openai.call(model="gpt-4o-mini", client=custom_client)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...


response = recommend_book("fantasy")
print(response.content)
```

In this example, we're creating a custom OpenAI client with a specific API key, organization ID, and base URL. This custom client is then passed to the call decorator, allowing us to use a custom endpoint or configuration for our LLM calls.

Any custom client is supported so long as it has the same API as the original base client.

## Handling Responses

??? api "API Documentation"

    [`mirascope.core.anthropic.call_response`](../api/core/anthropic/call_response.md)

    [`mirascope.core.cohere.call_response`](../api/core/cohere/call_response.md)

    [`mirascope.core.gemini.call_response`](../api/core/gemini/call_response.md)

    [`mirascope.core.groq.call_response`](../api/core/groq/call_response.md)

    [`mirascope.core.mistral.call_response`](../api/core/mistral/call_response.md)

    [`mirascope.core.openai.call_response`](../api/core/openai/call_response.md)

When you make a call to an LLM using Mirascope's `call` decorator, the response is wrapped in a provider-specific `BaseCallResponse` object (e.g. `OpenAICallResponse`). This object provides a consistent interface for accessing the response data across different providers while still offering access to provider-specific details.

### Common Response Properties and Methods

All `BaseCallResponse` objects share these common properties:

- `content`: The main text content of the response. If no content is present, this will be the empty string.
- `finish_reasons`: A list of reasons why the generation finished (e.g., "stop", "length"). These will be typed specifically for the provider used. If no finish reasons are present, this will be `None`.
- `model`: The name of the model used for generation.
- `id`: A unique identifier for the response if available. Otherwise this will be `None`.
- `usage`: Information about token usage for the call if available. Otherwise this will be `None`.
- `input_tokens`: The number of input tokens used if available. Otherwise this will be `None`.
- `output_tokens`: The number of output tokens generated if available. Otherwise this will be `None`.
- `cost`: An estimated cost of the API call if available. Otherwise this will be `None`.
- `message_param`: The assistant's response formatted as a message parameter.
- `tools`: A list of provider-specific tools used in the response, if any. Otherwise this will be `None`. Check out the [`Tools`](./tools.md) documentation for more details.
- `tool`: The first tool used in the response, if any. Otherwise this will be `None`. Check out the [`Tools`](./tools.md) documentation for more details.
- `tool_types`: A list of tool types used in the call, if any. Otherwise this will be `None`.
- `prompt_template`: The prompt template used for the call.
- `fn_args`: The arguments passed to the function.
- `dynamic_config`: The dynamic configuration used for the call.
- `metadata`: Any metadata provided using the dynamic configuration.
- `messages`: The list of messages sent in the request.
- `call_params`: The call parameters provided to the `call` decorator.
- `call_kwargs`: The finalized keyword arguments used to make the API call.
- `user_message_param`: The most recent user message, if any. Otherwise this will be `None`.
- `start_time`: The timestamp when the call started.
- `end_time`: The timestamp when the call ended.

There are also two common methods:

- `__str__`: Returns the `content` property of the response for easy printing.
- `tool_message_params`: Creates message parameters for tool call results. Check out the [`Tools`](./tools.md) documentation for more information.

### Provider-Specific Response Details

While Mirascope provides a consistent interface, you can also always access the full, provider-specific response object if needed. This is available through the `response` property of the `BaseCallResponse` object.

```python
# Accessing OpenAI-specific chat completion details
completion = response.response
print(f"Content: {completion.choices[0].message.content}")
```

!!! note "Reasoning For Provider-Specific `BaseCallResponse` Objects"

    The reason that we have provider-specific response objects (e.g. `OpenAICallResponse`) is to provide proper type hints and safety when accessing the original response.

### Error Handling

When making LLM calls, it's important to handle potential errors. Mirascope preserves the original error messages from providers, allowing you to catch and handle them appropriately:

```python
from openai import OpenAIError
from mirascope.core import openai, prompt_template

@openai.call(model="gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str):
    ...

try:
    response = recommend_book("fantasy")
    print(response.content)
except OpenAIError as e:
    print(f"Error: {str(e)}")
```

By catching provider-specific errors, you can implement appropriate error handling and fallback strategies in your application. You can of course always catch the base `Exception` instead of provider-specific exceptions.

### Type Safety and Proper Hints

One of the primary benefits of Mirascope is the enhanced type safety and proper type hints provided by the `call` decorator. This feature ensures that your IDE and type checker can accurately infer the return types of your LLM calls based on the parameters you've set.

For example:

- When using a basic call, the output will be properly typed as the provider-specific call response.
- When you set a `response_model`, the output will be properly typed as the `ResponseModelT` type of the `response_model` you passed in.
- When streaming is enabled, the return type will reflect the stream type.
- If you use an `output_parser`, the return type will match the parser's output type.

This type safety extends across all the different settings of the `call` decorator, providing a robust development experience and helping to catch potential type-related errors early in the development process.

![calls-type-hint](../assets/calls-type-hint.png)

In this example, your IDE will provide proper autocompletion and type checking for `recommendation.content` and `recommendation.response`, enhancing code reliability and developer productivity.

## Best Practices

To make the most of Mirascope's `call` decorator and ensure you're building robust, efficient, and maintainable LLM applications, consider the following best practices:

- **Provider Flexibility**: Design functions to be provider-agnostic, allowing easy switching between different LLM providers for comparison or fallback strategies.
   ```python
   @prompt_template("Recommend a {genre} book")
   def recommend_book(genre: str):
       ...

   # Can easily switch between providers
   openai_response = recommend_book.run(openai.call("gpt-4o-mini"))("fantasy")
   anthropic_response = recommend_book.run(anthropic.call("claude-3-5-sonnet-20240620"))("fantasy")
   ```

- **Provider-Specific Prompts**: When necessary, tailor prompts to leverage unique features of specific providers using provider-specific `call` decorators. For example, Anthropic's Claude model is known to handle prompts with XML particularly well.
   ```python
   @anthropic.call("claude-3-5-sonnet-20240620")
   @prompt_template(
       """
       <task>Recommend a {genre} book</task>
       <format>
         <title>Book Title</title>
         <author>Author Name</author>
         <description>Brief description</description>
       </format>
       """
   )
   def recommend_book_claude(genre: str):
       ...
   ```

- **Error Handling**: Implement robust error handling to manage API failures, timeouts, or content policy violations, ensuring your application's resilience.
   ```python
   from openai import OpenAIError
   from anthropic import AnthropicError

   try:
       response = recommend_book("fantasy")
   except OpenAIError as e:
       print(f"OpenAI error: {e}")
       # Fallback to another provider or retry logic
   except AnthropicError as e:
       print(f"Anthropic error: {e}")
       # Fallback to another provider or retry logic
   except Exception as e:
       print(f"Unexpected error: {e}")
       # General error handling
   ```

   For more advanced retry logic, check out our documentation on [using Tenacity](../integrations/tenacity.md).

- **Streaming for Long Tasks**: Utilize streaming for long-running tasks or when providing real-time updates to users, improving the user experience.
   ```python
   @openai.call("gpt-4o-mini", stream=True)
   @prompt_template("Summarize this book: {title}")
   def summarize_book(title: str):
       ...

   for chunk, _ in summarize_book("The Lord of the Rings"):
       print(chunk.content, end="", flush=True)
   ```

   For more details on streaming, check out the [`Streams`](./streams.md) documentation.

- **Modular Function Design**: Break down complex tasks into smaller, modular functions that can be chained together, enhancing reusability and maintainability.
   ```python
   @openai.call("gpt-4o-mini")
   @prompt_template("Summarize this text: {text}")
   def summarize(text: str):
       ...

   @openai.call("gpt-4o-mini")
   @prompt_template("Translate this text to {language}: {summary}")
   def translate(summary: str, language: str):
       ...

   def summarize_and_translate(original_text: str, target_language: str):
       summary = summarize(original_text)
       return translate(summary.content, target_language)
   ```

   For more on chaining, see the [`Chaining`](./chaining.md) documentation.

- **Custom Clients**: Leverage custom clients when working with self-hosted models or specific API configurations, allowing for greater flexibility in deployment scenarios.
   ```python
   from openai import OpenAI

   custom_client = OpenAI(
       api_key="your-api-key",
       base_url="https://your-custom-endpoint.com/v1"
   )

   @openai.call("gpt-4o-mini", client=custom_client)
   @prompt_template("Recommend a {genre} book")
   def recommend_book(genre: str):
       ...
   ```

   This approach allows you to use open-source models by serving OpenAI compatible endpoints (e.g., with `vLLM`, `Ollama`, etc).

- **Structured Outputs**: Use `response_models` to ensure consistency and type safety when you need structured data from your LLM calls.
   ```python
   from pydantic import BaseModel

   class BookRecommendation(BaseModel):
       title: str
       author: str

   @openai.call("gpt-4o-mini", response_model=BookRecommendation)
   @prompt_template("Recommend a {genre} book")
   def recommend_book(genre: str):
       ...

   recommendation = recommend_book("fantasy")
   print(f"Title: {recommendation.title}")
   print(f"Author: {recommendation.author}")
   ```

   For more details, check out the [`Response Models`](./response_models.md) documentation.

- **Parameterized Calls**: Take advantage of `call_params` to customize model behavior without changing your core function logic.
   ```python
   @openai.call("gpt-4o-mini", call_params={"temperature": 0.7, "max_tokens": 150})
   @prompt_template("Write a short poem about {topic}")
   def write_poem(topic: str):
       ...
   ```

By following these best practices, you can create more robust, flexible, and efficient LLM applications with Mirascope. Remember that mastering the `call` decorator is key to building applications that are adaptable to various providers and use cases.