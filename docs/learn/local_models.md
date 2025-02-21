---
search:
  boost: 3
---

# Local (Open-Source) Models

{% set local_providers = [("Ollama", "https://github.com/ollama/ollama/blob/main/docs/openai.md"), ("vLLM", "https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html")] %}

You can use the [`llm.call`](../api/llm/call.md) decorator to interact with models running with [Ollama](https://github.com/ollama/ollama) or [vLLM](https://github.com/vllm-project/vllm):

!!! mira ""

    {% for provider, _ in local_providers %}
    === "{{ provider }}"

        ```python hl_lines="5 20"
        --8<-- "examples/learn/local_models/{{ provider.lower() }}.py"
        ```

    {% endfor %}

??? info "Double Check Support"

    The `llm.call` decorator uses OpenAI compatibility under the hood. Of course, not all open-source models or providers necessarily support all of OpenAI's available features, but most use-cases are generally available. See the links we've included below for more details:

    {% for provider, support_url in local_providers %}
    - [{{ provider }} OpenAI Compatibility]({{ support_url }})
    {% endfor %}

## OpenAI Compatibility

When hosting (fine-tuned) open-source LLMs yourself locally or in your own cloud with tools that have OpenAI compatibility, you can use the [`openai.call`](../api/core/openai/call.md) decorator with a [custom client](./calls.md#custom-client) to interact with your model using all of Mirascope's various features.

!!! mira ""

    {% for provider, _ in local_providers %}
    === "{{ provider }}"

        ```python hl_lines="5-8 11 26"
        --8<-- "examples/learn/local_models/openai_compatibility/{{ provider.lower() }}.py"
        ```
    
    {% endfor %}
