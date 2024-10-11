# Calls

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on writing [Prompts](./prompts.md)
    </div>

When working with Large Language Model (LLM) APIs in Mirascope, a "call" refers to making a request to a LLM provider's API with a particular setting and prompt.

The `call` decorator is a core feature of the Mirascope library, designed to simplify and streamline interactions with various LLM providers. This powerful tool allows you to transform prompt templates written as Python functions into LLM API calls with minimal boilerplate code while providing type safety and consistency across different providers.

We currently support [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Mistral](https://mistral.ai/), [Gemini](https://gemini.google.com), [Groq](https://groq.com/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Vertex AI](https://cloud.google.com/vertex-ai)

If there are any providers we don't yet support that you'd like to see supported, let us know!

??? api "API Documentation"

    {% for provider in supported_llm_providers %}
    [`mirascope.core.{{ provider | provider_dir }}.call`](../api/core/{{ provider | provider_dir}}/call.md)
    {% endfor %}

## Basic Usage and Syntax

### Provider-Specific Usage

Let's take a look at a basic example using Mirascope vs. official provider SDKs:

!!! mira "Mirascope"

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="4 5"
            {% else %}
            ```python hl_lines="4 6"
            {% endif %}
            --8<-- "examples/learn/calls/basic_usage/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

??? note "Official SDK"

    {% for provider in supported_llm_providers %}
    === "{{ provider }}"

        {% if provider == "Anthropic" %}
        ```python hl_lines="7-13"
        {% elif provider in ["Gemini", "Vertex AI"] %}
        ```python hl_lines="7-10"
        {% elif provider == "LiteLLM" %}
        ```python hl_lines="5-9"
        {% elif provider == "Azure AI" %}
        ```python hl_lines="11-18"
        {% else %}
        ```python hl_lines="7-11"
        {% endif %}
        --8<-- "examples/learn/calls/basic_usage/{{ provider | provider_dir }}/official_sdk_call.py"
        ```

    {% endfor %}

Notice how Mirascope makes calls more readable by reducing boilerplate and standardizing interactions with LLM providers.

In these above Mirascope examples, we are directly tying the prompt to a specific provider and call setting (provider-specific prompt engineering). In these cases, the `@prompt_template` decorator becomes optional unless you're using string templates.

### Provider-Agnostic Usage

We've implemented calls as decorators so that they work for both provider-specific cases (as seen above) as well as provider-agnostic cases.

Let's take a look at a basic example using Mirascope to call both OpenAI and Anthropic with the same prompt:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "string_template" %}
        ```python hl_lines="4-5 10 16"
        {% else %}
        ```python hl_lines="4-6 11 17"
        {% endif %}
        --8<-- "examples/learn/calls/basic_usage/provider_agnostic/{{ method }}.py"
        ```
    {% endfor %}

## Handling Responses

### Common Response Properties and Methods

??? api "API Documentation"

    [`mirascope.core.base.call_response`](../api/core/base/call_response.md)

All [`BaseCallResponse`](../api/core/base/call_response.md) objects share these common properties:

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

??? api "API Documentation"

    {% for provider in supported_llm_providers %}
    {% if provider == "LiteLLM" %}
    [`mirascope.core.litellm.call_response`](../api/core/openai/call_response.md)
    {% else %}
    [`mirascope.core.{{ provider | provider_dir }}.call_response`](../api/core/{{ provider | provider_dir }}/call_response.md)
    {% endif %}
    {% endfor %}

While Mirascope provides a consistent interface, you can also always access the full, provider-specific response object if needed. This is available through the `response` property of the `BaseCallResponse` object.

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"
        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="10"
            --8<-- "examples/learn/calls/basic_usage/{{ provider | provider_dir }}/{{ method }}.py::9"
            original_response = response.response
            ```

        {% endfor %}
    {% endfor %}

!!! note "Reasoning For Provider-Specific `BaseCallResponse` Objects"

    The reason that we have provider-specific response objects (e.g. `OpenAICallResponse`) is to provide proper type hints and safety when accessing the original response.

## Common Parameters Across Providers

While each LLM provider has its own specific parameters, there are several common parameters that you'll find across all providers when using the `call` decorator. These parameters allow you to control various aspects of the LLM call:

- `model`: The only required parameter for all providers, which may be passed in as a standard argument (whereas all others are optional and must be provided as keyword arguments). It specifies which language model to use for the generation. Each provider has its own set of available models.
- `stream`: A boolean that determines whether the response should be streamed or returned as a complete response. We cover this in more detail in the [`Streams`](./streams.md) documentation.
- `response_model`: A Pydantic `BaseModel` type that defines how to structure the response. We cover this in more detail in the [`Response Models`](./response_models.md) documentation.
- `output_parser`: A function for parsing the response output. We cover this in more detail in the [`Output Parsers`](./output_parsers.md) documentation.
- `json_mode`: A boolean that deterines whether to use JSON mode or not. We cover this in more detail in the [`JSON Mode`](./json_mode.md) documentation.
- `tools`: A list of tools that the model may request to use in its response. We cover this in more detail in the [`Tools`](./tools.md) documentation.
- `client`: A custom client to use when making the call to the LLM. We cover this in more detail in the [`Custom Client`](#custom-client) section below.
- `call_params`: The provider-specific parameters to use when making the call to that provider's API. We cover this in more detail in the [`Provider-Specific Parameters`](#provider-specific-parameters) section below.

These common parameters provide a consistent way to control the behavior of LLM calls across different providers. Keep in mind that while these parameters are widely supported, there might be slight variations in how they're implemented or their exact effects across different providers (and the documentation should cover any such differences).

## Provider-Specific Parameters

??? api "API Documentation"

    {% for provider in supported_llm_providers %}
    {% if provider == "LiteLLM" %}
    [`mirascope.core.litellm.call_params`](../api/core/openai/call_params.md)
    {% else %}
    [`mirascope.core.{{ provider | provider_dir }}.call_params`](../api/core/{{ provider | provider_dir }}/call_params.md)
    {% endif %}
    {% endfor %}

While Mirascope provides a consistent interface across different LLM providers, each provider has its own set of specific parameters that can be used to further configure the behavior of the model. These parameters are passed to the `call` decorator through the `call_params` argument.

For all providers, we have only included additional call parameters that are not already covered as shared arguments to the `call` decorator (e.g. `model`). We have also opted to exclude currently deprecated parameters entirely. However, since `call_params` is just a `TypedDict`, you can always include any additional keys at the expense of type errors (and potentially unknown behavior).

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"
        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if provider == "Gemini" %}
            ```python hl_lines="1 7"
            {% elif provider == "Vertex AI" %}
            ```python hl_lines="2 7"
            {% else %}
            ```python hl_lines="4"
            {% endif %}
            --8<-- "examples/learn/calls/call_params/{{ provider | provider_dir }}/{{ method }}.py::9"
            ```

        {% endfor %}
    {% endfor %}

## Dynamic Configuration

Often you will want (or need) to configure your calls dynamically at runtime. Mirascope supports returning a `BaseDynamicConfig` from your prompt template, which will then be used to dynamically update the settings of the call.

In all cases, you will need to return your prompt messages through the `messages` keyword of the dynamic config unless you're using string templates.

### Call Params

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == 'string_template' %}
            ```python hl_lines="5 8"
            {% elif method == "base_message_param" %}
            ```python hl_lines="7-10"
            {% else %}
            ```python hl_lines="7 8"
            {% endif %}
            --8<-- "examples/learn/calls/dynamic_configuration/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

### Metadata

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == 'string_template' %}
            ```python hl_lines="5 9"
            {% elif method == "base_message_param" %}
            ```python hl_lines="7-9 11"
            {% else %}
            ```python hl_lines="7 9"
            {% endif %}
            --8<-- "examples/learn/calls/dynamic_configuration/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

## Custom Messages

You can also always return the original message types for any provider. To do so, simply return the provider-specific dynamic config:

!!! mira ""

    {% for provider in supported_llm_providers %}
    === "{{ provider }}"

        {% if provider == "Vertex AI" %}
        ```python hl_lines="8-10"
        {% elif provider in ["Mistral", "Cohere", "Azure AI"] %}
        ```python hl_lines="7"
        {% else %}
        ```python hl_lines="6"
        {% endif %}
        --8<-- "examples/learn/calls/custom_messages/{{ provider | provider_dir }}_messages.py"
        ```
    {% endfor %}

## Custom Client

Mirascope allows you to use custom clients when making calls to LLM providers. This feature is particularly useful when you need to use specific client configurations, handle authentication in a custom way, or work with self-hosted models.

To use a custom client, you can pass it to the `call` decorator using the `client` parameter. Here's an example using a custom OpenAI client:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"
        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if provider == "LiteLLM" %}
            ```python
            {% elif provider in ["OpenAI", "Mistral", "Vertex AI"] %}
            ```python hl_lines="2 5"
            {% elif provider == "Azure AI" %}
            ```python hl_lines="1-2 8-10"
            {% elif provider == "Bedrock" %}
            ```python hl_lines="1 6"
            {% else %}
            ```python hl_lines="1 5"
            {% endif %}
            --8<-- "examples/learn/calls/custom_client/{{ provider | provider_dir }}/{{ method }}.py"
            ```

        {% endfor %}
    {% endfor %}

!!! warning "Make sure to use the correct client!"

    A common mistake is to use the synchronous client with async calls. Read the section on [Async Custom Client](./async.md#custom-client) to see how to use a custom client with asynchronous calls.

## Error Handling

When making LLM calls, it's important to handle potential errors. Mirascope preserves the original error messages from providers, allowing you to catch and handle them appropriately:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"
        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if provider in ["Gemini", "Azure AI", "Vertex AI"] %}
            ```python hl_lines="9 12"
            {% elif provider == "Mistral" %}
            ```python hl_lines="2 10 13 16"
            {% elif provider == "OpenAI" %}
            ```python hl_lines="2 10 13"
            {% else %}
            ```python hl_lines="1 10 13"
            {% endif %}
            --8<-- "examples/learn/calls/error_handling/{{ provider | provider_dir }}/{{ method }}.py"
            ```

        {% endfor %}
    {% endfor %}

By catching provider-specific errors, you can implement appropriate error handling and fallback strategies in your application. You can of course always catch the base Exception instead of provider-specific exceptions (which we needed to do in some of our examples due to not being able to find the right exceptions to catch for those providers...).

## Next Steps

By mastering calls in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend choosing one of:

- [Streams](./streams.md) to see how to stream call responses for a more real-time interaction.
- [Chaining](./chaining.md) to see how to chain calls together.
- [Response Models](./response_models.md) to see how to generate structured outputs.
- [Tools](./tools.md) to see how to give LLMs access to custom tools to extend their capabilities.
- [Async](./async.md) to see how to better take advantage of asynchronous programming and parallelization for improved performance.

Pick whichever path aligns best with what you're hoping to get from Mirascope.
