---
search:
  boost: 3
---

# Open-Source Models

Many local open-source model hosts (like [Ollama](https://github.com/ollama/ollama) & [vLLM](https://github.com/vllm-project/vllm)) have compatibility to the OpenAI API.
This allows you to use all of their features via the OpenAI integration, but not all OpenAI features are available.

For most usecases this should suffice. In Ollama, there is support for structures responses, vision, tools, and streaming - just to name a few.

Please consult the links below to see what features are supported by your local model provider.


## Usage 

Ollama hosts its API locally, so all you need to do is overwrite the URL the OpenAI integration uses.
This is easily done by passing a [custom client](./calls.md#custom-client) to the `@openai.call()` decorator, like shown below.

!!! mira ""

    {% for method, support_url in [("Ollama", "https://github.com/ollama/ollama/blob/main/docs/openai.md"), ("vLLM", "https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html")] %}
    === "{{ method }}"
        
        !!! info "OpenAI API Compatibility"
        
            [Click here for {{ method }} OpenAI compatibility info]({{ support_url }})

        ```python hl_lines="7 9"
        --8<-- "examples/learn/local_models/{{ method.lower() }}.py"
        ```
    {% endfor %}

