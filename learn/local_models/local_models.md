---
search:
  boost: 3
---

# Local (Open-Source) Models

When hosting (fine-tuned) open-source LLMs yourself locally or in your own cloud with tools that have OpenAI compatibility (e.g. [Ollama](https://github.com/ollama/ollama), [vLLM](https://github.com/vllm-project/vllm), etc.), you can use the [`openai.call`](../api/core/openai/call.md) method with a [custom client](./calls.md#custom-client) to interact with your model using all of Mirascope's various features.

Of course, not all open-source models or providers necessarily support all of OpenAI's available features, but most use-cases are generally available. Se the links we've included in each usage example below for more details.

!!! mira ""

    {% for method, support_url in [("Ollama", "https://github.com/ollama/ollama/blob/main/docs/openai.md"), ("vLLM", "https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html")] %}
    === "{{ method }}"

        !!! info ""

            [{{ method }} OpenAI Compatibility]({{ support_url }})

        ```python hl_lines="5-8 11 26"
        --8<-- "examples/learn/local_models/{{ method.lower() }}.py"
        ```
    
    {% endfor %}
