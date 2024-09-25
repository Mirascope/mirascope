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

    [`mirascope.core.anthropic.call`](../api/core/anthropic/call.md)

    [`mirascope.core.azure.call`](../api/core/azure/call.md)

    [`mirascope.core.cohere.call`](../api/core/cohere/call.md)

    [`mirascope.core.gemini.call`](../api/core/gemini/call.md)

    [`mirascope.core.groq.call`](../api/core/groq/call.md)

    [`mirascope.core.litellm.call`](../api/core/litellm/call.md)

    [`mirascope.core.mistral.call`](../api/core/mistral/call.md)

    [`mirascope.core.openai.call`](../api/core/openai/call.md)

    [`mirascope.core.vertex.call`](../api/core/vertex/call.md)

## Basic Usage & Syntax

### Provider-Specific

Let's take a look at a basic example using Mirascope vs. official provider SDKs:

!!! mira "Mirascope"

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/openai/shorthand.py"
            ```

        === "Anthropic"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/anthropic/shorthand.py"
            ```

        === "Mistral"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/mistral/shorthand.py"
            ```

        === "Gemini"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/gemini/shorthand.py"
            ```

        === "Groq"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/groq/shorthand.py"
            ```

        === "Cohere"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/cohere/shorthand.py"
            ```

        === "LiteLLM"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/litellm/shorthand.py"
            ```

        === "Azure AI"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/azure/shorthand.py"
            ```
    
        === "Vertex AI"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/vertex/shorthand.py"
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/openai/messages.py"
            ```

        === "Anthropic"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/anthropic/messages.py"
            ```

        === "Mistral"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/mistral/messages.py"
            ```

        === "Gemini"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/gemini/messages.py"
            ```

        === "Groq"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/groq/messages.py"
            ```

        === "Cohere"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/cohere/messages.py"
            ```

        === "LiteLLM"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/litellm/messages.py"
            ```

        === "Azure AI"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/azure/messages.py"
            ```
    
        === "Vertex AI"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/vertex/messages.py"
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="4 5"
            --8<-- "examples/learn/calls/basic_call/openai/string_template.py"
            ```

        === "Anthropic"

            ```python hl_lines="4 5"
            --8<-- "examples/learn/calls/basic_call/anthropic/string_template.py"
            ```

        === "Mistral"

            ```python hl_lines="4 5"
            --8<-- "examples/learn/calls/basic_call/mistral/string_template.py"
            ```

        === "Gemini"

            ```python hl_lines="4 5"
            --8<-- "examples/learn/calls/basic_call/gemini/string_template.py"
            ```

        === "Groq"

            ```python hl_lines="4 5"
            --8<-- "examples/learn/calls/basic_call/groq/string_template.py"
            ```

        === "Cohere"

            ```python hl_lines="4 5"
            --8<-- "examples/learn/calls/basic_call/cohere/string_template.py"
            ```

        === "LiteLLM"

            ```python hl_lines="4 5"
            --8<-- "examples/learn/calls/basic_call/litellm/string_template.py"
            ```

        === "Azure AI"

            ```python hl_lines="4 5"
            --8<-- "examples/learn/calls/basic_call/azure/string_template.py"
            ```
    
        === "Vertex AI"

            ```python hl_lines="4 5"
            --8<-- "examples/learn/calls/basic_call/vertex/string_template.py"
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/openai/base_message_param.py"
            ```

        === "Anthropic"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/anthropic/base_message_param.py"
            ```

        === "Mistral"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/mistral/base_message_param.py"
            ```

        === "Gemini"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/gemini/base_message_param.py"
            ```

        === "Groq"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/groq/base_message_param.py"
            ```

        === "Cohere"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/cohere/base_message_param.py"
            ```

        === "LiteLLM"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/litellm/base_message_param.py"
            ```

        === "Azure AI"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/azure/base_message_param.py"
            ```
    
        === "Vertex AI"

            ```python hl_lines="4 6"
            --8<-- "examples/learn/calls/basic_call/vertex/base_message_param.py"
            ```

!!! note "Official SDK"

    === "OpenAI"

        ```python
        --8<-- "examples/learn/calls/basic_call/openai/official_sdk_call.py"
        ```

    === "Anthropic"

        ```python
        --8<-- "examples/learn/calls/basic_call/anthropic/official_sdk_call.py"
        ```

    === "Mistral"

        ```python
        --8<-- "examples/learn/calls/basic_call/mistral/official_sdk_call.py"
        ```

    === "Gemini"

        ```python
        --8<-- "examples/learn/calls/basic_call/gemini/official_sdk_call.py"
        ```

    === "Groq"

        ```python
        --8<-- "examples/learn/calls/basic_call/groq/official_sdk_call.py"
        ```

    === "Cohere"

        ```python
        --8<-- "examples/learn/calls/basic_call/cohere/official_sdk_call.py"
        ```

    === "LiteLLM"

        ```python
        --8<-- "examples/learn/calls/basic_call/litellm/official_sdk_call.py"
        ```

    === "Azure AI"

        ```python
        --8<-- "examples/learn/calls/basic_call/azure/official_sdk_call.py"
        ```
    
    === "Vertex AI"

        ```python
        --8<-- "examples/learn/calls/basic_call/vertex/official_sdk_call.py"
        ```

Notice how Mirascope makes calls more readable by reducing boilerplate and standardizing interactions with LLM providers.

In these above Mirascope examples, we are directly tying the prompt to a specific provider and call setting (provider-specific prompt engineering). In these cases, the `@prompt_template` decorator becomes optional unless you're using string templates.

### Provider-Agnostic Usage

We've implemented calls as decorators so that they work for both provider-specific cases (as seen above) as well as provider-agnostic cases.

Let's take a look at a basic example using Mirascope to call both OpenAI and Anthropic with the same prompt:

!!! mira ""

    === "Shorthand"

        ```python hl_lines="4-6 11 17"
        --8<-- "examples/learn/calls/basic_call/provider_agnostic/shorthand.py"
        ```

    === "Messages"

        ```python hl_lines="4-6 11 17"
        --8<-- "examples/learn/calls/basic_call/provider_agnostic/messages.py"
        ```

    === "String Template"

        ```python hl_lines="4-5 10 16"
        --8<-- "examples/learn/calls/basic_call/provider_agnostic/string_template.py"
        ```

    === "BaseMessageParam"

        ```python hl_lines="4-6 11 17"
        --8<-- "examples/learn/calls/basic_call/provider_agnostic/base_message_param.py"
        ```

## Handling Responses

??? api "API Documentation"

    [`mirascope.core.base.call_response`](../api/core/base/call_response.md)

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

??? api "API Documentation"

    [`mirascope.core.anthropic.call_response`](../api/core/anthropic/call_response.md)

    [`mirascope.core.azure.call_response`](../api/core/azure/call_response.md)

    [`mirascope.core.cohere.call_response`](../api/core/cohere/call_response.md)

    [`mirascope.core.gemini.call_response`](../api/core/gemini/call_response.md)

    [`mirascope.core.groq.call_response`](../api/core/groq/call_response.md)

    [`mirascope.core.litellm.call_response`](../api/core/openai/call_response.md)

    [`mirascope.core.mistral.call_response`](../api/core/mistral/call_response.md)

    [`mirascope.core.openai.call_response`](../api/core/openai/call_response.md)

    [`mirascope.core.vertex.call_response`](../api/core/vertex/call_response.md)


While Mirascope provides a consistent interface, you can also always access the full, provider-specific response object if needed. This is available through the `response` property of the `BaseCallResponse` object.

!!! mira ""

    === "OpenAI"

        ```python hl_lines="10-11"
        --8<-- "examples/learn/calls/provider_specific_response/openai_response.py"
        ```

    === "Anthropic"

        ```python hl_lines="10-11"
        --8<-- "examples/learn/calls/provider_specific_response/anthropic_response.py"
        ```

    === "Mistral"

        ```python hl_lines="10-11"
        --8<-- "examples/learn/calls/provider_specific_response/mistral_response.py"
        ```

    === "Gemini"

        ```python hl_lines="10-11"
        --8<-- "examples/learn/calls/provider_specific_response/gemini_response.py"
        ```

    === "Groq"

        ```python hl_lines="10-11"
        --8<-- "examples/learn/calls/provider_specific_response/groq_response.py"
        ```

    === "Cohere"

        ```python hl_lines="10-11"
        --8<-- "examples/learn/calls/provider_specific_response/cohere_response.py"
        ```

    === "LiteLLM"

        ```python hl_lines="10-11"
        --8<-- "examples/learn/calls/provider_specific_response/litellm_response.py"
        ```

    === "Azure AI"

        ```python hl_lines="10-11"
        --8<-- "examples/learn/calls/provider_specific_response/azure_response.py"
        ```

    === "Vertex AI"

        ```python hl_lines="10-11"
        --8<-- "examples/learn/calls/provider_specific_response/vertex_response.py"
        ```

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

    [`mirascope.core.anthropic.call_params`](../api/core/anthropic/call_params.md)

    [`mirascope.core.azure.call_params`](../api/core/azure/call_params.md)

    [`mirascope.core.cohere.call_params`](../api/core/cohere/call_params.md)

    [`mirascope.core.gemini.call_params`](../api/core/gemini/call_params.md)

    [`mirascope.core.groq.call_params`](../api/core/groq/call_params.md)

    [`mirascope.core.litellm.call_params`](../api/core/openai/call_params.md)

    [`mirascope.core.mistral.call_params`](../api/core/mistral/call_params.md)

    [`mirascope.core.openai.call_params`](../api/core/openai/call_params.md)

    [`mirascope.core.vertex.call_params`](../api/core/vertex/call_params.md)

While Mirascope provides a consistent interface across different LLM providers, each provider has its own set of specific parameters that can be used to further configure the behavior of the model. These parameters are passed to the `call` decorator through the `call_params` argument.

For all providers, we have only included additional call parameters that are not already covered as shared arguments to the `call` decorator (e.g. `model`). We have also opted to exclude currently deprecated parameters entirely. However, since `call_params` is just a `TypedDict`, you can always include any additional keys at the expense of type errors (and potentially unknown behavior).

!!! mira ""


    === "OpenAI"

        ```python hl_lines="4"
        --8<-- "examples/learn/calls/call_params/openai_call_params.py"
        ```

    === "Anthropic"

        ```python hl_lines="4"
        --8<-- "examples/learn/calls/call_params/anthropic_call_params.py"
        ```

    === "Mistral"

        ```python hl_lines="4"
        --8<-- "examples/learn/calls/call_params/mistral_call_params.py"
        ```

    === "Gemini"

        ```python hl_lines="1 7"
        --8<-- "examples/learn/calls/call_params/gemini_call_params.py"
        ```

    === "Groq"

        ```python hl_lines="4"
        --8<-- "examples/learn/calls/call_params/groq_call_params.py"
        ```

    === "Cohere"

        ```python hl_lines="4"
        --8<-- "examples/learn/calls/call_params/cohere_call_params.py"
        ```

    === "LiteLLM"

        ```python hl_lines="4"
        --8<-- "examples/learn/calls/call_params/litellm_call_params.py"
        ```

    === "Azure AI"

        ```python hl_lines="4"
        --8<-- "examples/learn/calls/call_params/azure_call_params.py"
        ```

    === "Vertex AI"

        ```python hl_lines="1 7"
        --8<-- "examples/learn/calls/call_params/vertex_call_params.py"
        ```

## Dynamic Configuration

Often you will want (or need) to configure your calls dynamically at runtime. Mirascope supports returning a `BaseDynamicConfig` from your prompt template, which will then be used to dynamically update the settings of the call.

In all cases, you will need to return your prompt messages through the `messages` keyword of the dynamic config unless you're using string templates.

### Call Params

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/openai/shorthand.py"
            ```

        === "Anthropic"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/anthropic/shorthand.py"
            ```

        === "Mistral"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/mistral/shorthand.py"
            ```

        === "Gemini"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/gemini/shorthand.py"
            ```

        === "Groq"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/groq/shorthand.py"
            ```

        === "Cohere"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/cohere/shorthand.py"
            ```

        === "LiteLLM"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/litellm/shorthand.py"
            ```

        === "Azure AI"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/azure/shorthand.py"
            ```

        === "Vertex AI"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/vertex/shorthand.py"
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/openai/messages.py"
            ```

        === "Anthropic"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/anthropic/messages.py"
            ```

        === "Mistral"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/mistral/messages.py"
            ```

        === "Gemini"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/gemini/messages.py"
            ```

        === "Groq"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/groq/messages.py"
            ```

        === "Cohere"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/cohere/messages.py"
            ```

        === "LiteLLM"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/litellm/messages.py"
            ```

        === "Azure AI"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/azure/messages.py"
            ```

        === "Vertex AI"

            ```python hl_lines="7 8"
            --8<-- "examples/learn/calls/dynamic_configuration/vertex/messages.py"
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="5 8"
            --8<-- "examples/learn/calls/dynamic_configuration/openai/string_template.py"
            ```

        === "Anthropic"

            ```python hl_lines="5 8"
            --8<-- "examples/learn/calls/dynamic_configuration/anthropic/string_template.py"
            ```

        === "Mistral"

            ```python hl_lines="5 8"
            --8<-- "examples/learn/calls/dynamic_configuration/mistral/string_template.py"
            ```

        === "Gemini"

            ```python hl_lines="5 8"
            --8<-- "examples/learn/calls/dynamic_configuration/gemini/string_template.py"
            ```

        === "Groq"

            ```python hl_lines="5 8"
            --8<-- "examples/learn/calls/dynamic_configuration/groq/string_template.py"
            ```

        === "Cohere"

            ```python hl_lines="5 8"
            --8<-- "examples/learn/calls/dynamic_configuration/cohere/string_template.py"
            ```

        === "LiteLLM"

            ```python hl_lines="5 8"
            --8<-- "examples/learn/calls/dynamic_configuration/litellm/string_template.py"
            ```

        === "Azure AI"

            ```python hl_lines="5 8"
            --8<-- "examples/learn/calls/dynamic_configuration/azure/string_template.py"
            ```

        === "Vertex AI"

            ```python hl_lines="5 8"
            --8<-- "examples/learn/calls/dynamic_configuration/vertex/string_template.py"
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7-10"
            --8<-- "examples/learn/calls/dynamic_configuration/openai/base_message_param.py"
            ```

        === "Anthropic"

            ```python hl_lines="7-10"
            --8<-- "examples/learn/calls/dynamic_configuration/anthropic/base_message_param.py"
            ```

        === "Mistral"

            ```python hl_lines="7-10"
            --8<-- "examples/learn/calls/dynamic_configuration/mistral/base_message_param.py"
            ```

        === "Gemini"

            ```python hl_lines="7-10"
            --8<-- "examples/learn/calls/dynamic_configuration/gemini/base_message_param.py"
            ```

        === "Groq"

            ```python hl_lines="7-10"
            --8<-- "examples/learn/calls/dynamic_configuration/groq/base_message_param.py"
            ```

        === "Cohere"

            ```python hl_lines="7-10"
            --8<-- "examples/learn/calls/dynamic_configuration/cohere/base_message_param.py"
            ```

        === "LiteLLM"

            ```python hl_lines="7-10"
            --8<-- "examples/learn/calls/dynamic_configuration/litellm/base_message_param.py"
            ```

        === "Azure AI"

            ```python hl_lines="7-10"
            --8<-- "examples/learn/calls/dynamic_configuration/azure/base_message_param.py"
            ```

        === "Vertex AI"

            ```python hl_lines="7-10"
            --8<-- "examples/learn/calls/dynamic_configuration/vertex/base_message_param.py"
            ```

### Metadata

!!! mira ""

    === "Shorthand"

        === "OpenAI"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/openai/shorthand.py"
            ```

        === "Anthropic"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/anthropic/shorthand.py"
            ```

        === "Mistral"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/mistral/shorthand.py"
            ```

        === "Gemini"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/gemini/shorthand.py"
            ```

        === "Groq"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/groq/shorthand.py"
            ```

        === "Cohere"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/cohere/shorthand.py"
            ```

        === "LiteLLM"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/litellm/shorthand.py"
            ```

        === "Azure AI"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/azure/shorthand.py"
            ```

        === "Vertex AI"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/vertex/shorthand.py"
            ```

    === "Messages"

        === "OpenAI"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/openai/messages.py"
            ```

        === "Anthropic"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/anthropic/messages.py"
            ```

        === "Mistral"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/mistral/messages.py"
            ```

        === "Gemini"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/gemini/messages.py"
            ```

        === "Groq"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/groq/messages.py"
            ```

        === "Cohere"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/cohere/messages.py"
            ```

        === "LiteLLM"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/litellm/messages.py"
            ```

        === "Azure AI"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/azure/messages.py"
            ```

        === "Vertex AI"

            ```python hl_lines="7 9"
            --8<-- "examples/learn/calls/dynamic_configuration/vertex/messages.py"
            ```

    === "String Template"

        === "OpenAI"

            ```python hl_lines="5 9"
            --8<-- "examples/learn/calls/dynamic_configuration/openai/string_template.py"
            ```

        === "Anthropic"

            ```python hl_lines="5 9"
            --8<-- "examples/learn/calls/dynamic_configuration/anthropic/string_template.py"
            ```

        === "Mistral"

            ```python hl_lines="5 9"
            --8<-- "examples/learn/calls/dynamic_configuration/mistral/string_template.py"
            ```

        === "Gemini"

            ```python hl_lines="5 9"
            --8<-- "examples/learn/calls/dynamic_configuration/gemini/string_template.py"
            ```

        === "Groq"

            ```python hl_lines="5 9"
            --8<-- "examples/learn/calls/dynamic_configuration/groq/string_template.py"
            ```

        === "Cohere"

            ```python hl_lines="5 9"
            --8<-- "examples/learn/calls/dynamic_configuration/cohere/string_template.py"
            ```

        === "LiteLLM"

            ```python hl_lines="5 9"
            --8<-- "examples/learn/calls/dynamic_configuration/litellm/string_template.py"
            ```

        === "Azure AI"

            ```python hl_lines="5 9"
            --8<-- "examples/learn/calls/dynamic_configuration/azure/string_template.py"
            ```

        === "Vertex AI"

            ```python hl_lines="5 9"
            --8<-- "examples/learn/calls/dynamic_configuration/vertex/string_template.py"
            ```

    === "BaseMessageParam"

        === "OpenAI"

            ```python hl_lines="7-9 11"
            --8<-- "examples/learn/calls/dynamic_configuration/openai/base_message_param.py"
            ```

        === "Anthropic"

            ```python hl_lines="7-9 11"
            --8<-- "examples/learn/calls/dynamic_configuration/anthropic/base_message_param.py"
            ```

        === "Mistral"

            ```python hl_lines="7-9 11"
            --8<-- "examples/learn/calls/dynamic_configuration/mistral/base_message_param.py"
            ```

        === "Gemini"

            ```python hl_lines="7-9 11"
            --8<-- "examples/learn/calls/dynamic_configuration/gemini/base_message_param.py"
            ```

        === "Groq"

            ```python hl_lines="7-9 11"
            --8<-- "examples/learn/calls/dynamic_configuration/groq/base_message_param.py"
            ```

        === "Cohere"

            ```python hl_lines="7-9 11"
            --8<-- "examples/learn/calls/dynamic_configuration/cohere/base_message_param.py"
            ```

        === "LiteLLM"

            ```python hl_lines="7-9 11"
            --8<-- "examples/learn/calls/dynamic_configuration/litellm/base_message_param.py"
            ```

        === "Azure AI"

            ```python hl_lines="7-9 11"
            --8<-- "examples/learn/calls/dynamic_configuration/azure/base_message_param.py"
            ```

        === "Vertex AI"

            ```python hl_lines="7-9 11"
            --8<-- "examples/learn/calls/dynamic_configuration/vertex/base_message_param.py"
            ```

## Custom Messages

You can also always return the original message types for any provider. To do so, simply return the provider-specific dynamic config:

!!! mira ""

    === "OpenAI"

        ```python hl_lines="6"
        --8<-- "examples/learn/calls/custom_messages/openai_messages.py"
        ```

    === "Anthropic"

        ```python hl_lines="6"
        --8<-- "examples/learn/calls/custom_messages/anthropic_messages.py"
        ```

    === "Mistral"

        ```python hl_lines="7"
        --8<-- "examples/learn/calls/custom_messages/mistral_messages.py"
        ```

    === "Gemini"

        ```python hl_lines="6"
        --8<-- "examples/learn/calls/custom_messages/gemini_messages.py"
        ```

    === "Groq"

        ```python hl_lines="6"
        --8<-- "examples/learn/calls/custom_messages/groq_messages.py"
        ```

    === "Cohere"

        ```python hl_lines="7"
        --8<-- "examples/learn/calls/custom_messages/cohere_messages.py"
        ```

    === "LiteLLM"

        ```python hl_lines="6"
        --8<-- "examples/learn/calls/custom_messages/litellm_messages.py"
        ```

    === "Azure AI"

        ```python hl_lines="7"
        --8<-- "examples/learn/calls/custom_messages/azure_messages.py"
        ```

    === "Vertex AI"

        ```python hl_lines="8-10"
        --8<-- "examples/learn/calls/custom_messages/vertex_messages.py"
        ```

## Custom Client

Mirascope allows you to use custom clients when making calls to LLM providers. This feature is particularly useful when you need to use specific client configurations, handle authentication in a custom way, or work with self-hosted models.

To use a custom client, you can pass it to the `call` decorator using the `client` parameter. Here's an example using a custom OpenAI client:

!!! mira ""

    === "OpenAI"

        ```python hl_lines="2 5 10"
        --8<-- "examples/learn/calls/custom_client/openai_client.py"
        ```

    === "Anthropic"

        ```python hl_lines="1 5 10"
        --8<-- "examples/learn/calls/custom_client/anthropic_client.py"
        ```

    === "Mistral"

        ```python hl_lines="2-3 6 11"
        --8<-- "examples/learn/calls/custom_client/mistral_client.py"
        ```

    === "Gemini"

        ```python hl_lines="2 5 10"
        --8<-- "examples/learn/calls/custom_client/gemini_client.py"
        ```

    === "Groq"

        ```python hl_lines="2 5 10"
        --8<-- "examples/learn/calls/custom_client/groq_client.py"
        ```

    === "Cohere"

        ```python hl_lines="2 5 10"
        --8<-- "examples/learn/calls/custom_client/cohere_client.py"
        ```

    === "LiteLLM"

        ```python hl_lines="2 5 10"
        --8<-- "examples/learn/calls/custom_client/litellm_client.py"
        ```

    === "Azure AI"

        ```python hl_lines="1-3 5 9-11 19-21"
        --8<-- "examples/learn/calls/custom_client/azure_client.py"
        ```

    === "Vertex AI"

        ```python hl_lines="2 5 10"
        --8<-- "examples/learn/calls/custom_client/vertex_client.py"
        ```

## Error Handling

When making LLM calls, it's important to handle potential errors. Mirascope preserves the original error messages from providers, allowing you to catch and handle them appropriately:

!!! mira ""

    === "OpenAI"

        ```python hl_lines="2 10 13"
        --8<-- "examples/learn/calls/error_handling/openai_error.py"
        ```

    === "Anthropic"

        ```python hl_lines="1 10 13"
        --8<-- "examples/learn/calls/error_handling/anthropic_error.py"
        ```

    === "Mistral"

        ```python hl_lines="2 10 13 16"
        --8<-- "examples/learn/calls/error_handling/mistral_error.py"
        ```

    === "Gemini"

        ```python hl_lines="9 12"
        --8<-- "examples/learn/calls/error_handling/gemini_error.py"
        ```

    === "Groq"

        ```python hl_lines="1 10 13 16"
        --8<-- "examples/learn/calls/error_handling/groq_error.py"
        ```

    === "Cohere"

        ```python hl_lines="1 10 13 15"
        --8<-- "examples/learn/calls/error_handling/cohere_error.py"
        ```

    === "LiteLLM"

        ```python hl_lines="1 10 13 15"
        --8<-- "examples/learn/calls/error_handling/litellm_error.py"
        ```

    === "Azure AI"

        ```python hl_lines="9 12"
        --8<-- "examples/learn/calls/error_handling/azure_error.py"
        ```

    === "Vertex AI"

        ```python hl_lines="9 12"
        --8<-- "examples/learn/calls/error_handling/vertex_error.py"
        ```

By catching provider-specific errors, you can implement appropriate error handling and fallback strategies in your application. You can of course always catch the base Exception instead of provider-specific exceptions (which we needed to do in some of our examples due to not being able to find the right exceptions to catch for those providers...).

## Next Steps

By mastering calls in Mirascope, you'll be well-equipped to build robust, flexible, and reusable LLM applications.

Next, we recommend taking a look at the [Streams](./streams.md) documentation, which shows you how to stream your call responses for a more real-time interaction.
