# Mirascope

<p align="left">
    <a href="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests"/></a>
    <a href="https://codecov.io/github/Mirascope/mirascope" target="_blank"><img src="https://codecov.io/github/Mirascope/mirascope/graph/badge.svg?token=HAEAWT3KC9" alt="Coverage"/></a>
    <a href="https://mirascope.com/WELCOME" target="_blank"><img src="https://img.shields.io/badge/docs-available-brightgreen" alt="Docs"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/v/mirascope.svg" alt="PyPI Version"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/pyversions/mirascope.svg" alt="Stars"/></a>
    <a href="https://github.com/Mirascope/mirascope/blob/dev/LICENSE"><img src="https://img.shields.io/github/license/Mirascope/mirascope.svg" alt="License"/></a>
</p>

Mirascope is a powerful, flexible, and user-friendly library that simplifies the process of working with LLMs through a unified interface that works across various supported providers, including [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Mistral](https://mistral.ai/), [Google (Gemini/Vertex)](https://googleapis.github.io/python-genai/), [Groq](https://groq.com/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Bedrock](https://aws.amazon.com/bedrock/).

Whether you're generating text, extracting structured information, or developing complex AI-driven agent systems, Mirascope provides the tools you need to streamline your development process and create powerful, robust applications.

[:material-lightbulb: Why Use Mirascope](./WHY.md){: .md-button }
[:material-account-group: Join Our Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA){: .md-button }
[:material-star: Star the Repo](https://github.com/Mirascope/mirascope){: .md-button }  

## 30 Second Quickstart

Install Mirascope, specifying the provider(s) you intend to use, and set your API key:

{% set operating_systems = ["MacOS / Linux", "Windows"] %}
{% for os in operating_systems %}
=== "{{ os }}"

    {% for provider in supported_llm_providers %}
    === "{{ provider }}"

        ```bash
        pip install "mirascope[{{ provider | provider_dir }}]"
        {% if provider == "Gemini" %}
        {% if os == "Windows" %}set GOOGLE_API_KEY=XXXXX
        {% else %}export GOOGLE_API_KEY=XXXXX
        {% endif %}
        {% elif provider == "Cohere" %}
        {% if os == "Windows" %}set CO_API_KEY=XXXXX
        {% else %}export CO_API_KEY=XXXXX
        {% endif %}
        {% elif provider == "LiteLLM" %}
        {% if os == "Windows" %}set OPENAI_API_KEY=XXXXX 
        {% else %}export OPENAI_API_KEY=XXXXX 
        {% endif %}
        {% elif provider == "Azure AI" %}
        {% if os == "Windows" %}set AZURE_INFERENCE_ENDPOINT=XXXXX
        set AZURE_INFERENCE_CREDENTIAL=XXXXX
        {% else %}export AZURE_INFERENCE_ENDPOINT=XXXXX
        export AZURE_INFERENCE_CREDENTIAL=XXXXX
        {% endif %}
        {% elif provider == "Vertex AI" %}
        gcloud init
        gcloud auth application-default login
        {% elif provider == "Bedrock" %}
        aws configure
        {% else %}
        {% if os == "Windows" %}set {{ upper(provider | provider_dir) }}_API_KEY=XXXXX
        {% else %}export {{ upper(provider | provider_dir) }}_API_KEY=XXXXX
        {% endif %}
        {% endif %}
        ```
    {% endfor %}
{% endfor %}

Make your first call to an LLM to extract the title and author of a book from the given text:

!!! mira "Mirascope"

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="10 15 17"
            --8<-- "build/snippets/learn/response_models/basic_usage/{{ provider | provider_dir }}/{{ method }}.py:3:7"
            --8<-- "build/snippets/learn/response_models/basic_usage/{{ provider | provider_dir }}/{{ method }}.py:10:21"
            ```
        {% endfor %}

    {% endfor %}

??? note "Official SDK"

    {% for provider in supported_llm_providers %}
    === "{{ provider }}"

        {% if provider == "Anthropic" %}
        ```python hl_lines="19-38 43"
        {% elif provider == "Mistral" %}
        ```python hl_lines="21-46 51"
        {% elif provider == "Google" %}
        ```python hl_lines="20-60 65"
        {% elif provider == "Cohere" %}
        ```python hl_lines="19-36 41"
        {% elif provider == "LiteLLM" %}
        ```python hl_lines="16-37 42"
        {% elif provider == "Azure AI" %}
        ```python hl_lines="26-46 51"
        {% else %}
        ```python hl_lines="18-39 44"
        {% endif %}
        --8<-- "examples/learn/response_models/basic_usage/official_sdk/{{ provider | provider_dir }}_sdk.py"
        ```

    {% endfor %}

## Choose Your Path

### Tutorials

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Quickstart Guide__

    ---

    Comprehensive overview of core features and building blocks

    [:octicons-arrow-right-24: Quickstart](./tutorials/getting_started/quickstart.ipynb)

-   :material-database:{ .lg .middle } __Structured Outputs__

    ---

    Explore various techniques for generating structured outputs

    [:octicons-arrow-right-24: Structured Outputs](./tutorials/getting_started/structured_outputs.ipynb)

-   :material-link-variant:{ .lg .middle } __Dynamic Configuration & Chaining__

    ---

    Examples ranging from basic usage to more complex chaining techniques

    [:octicons-arrow-right-24: Dynamic Configuration & Chaining](./tutorials/getting_started/dynamic_configuration_and_chaining.ipynb)

-   :material-tools:{ .lg .middle } __Tools & Agents__

    ---

    Learn how to define tools for your LLM to build advanced AI agents

    [:octicons-arrow-right-24: Tools & Agents](./tutorials/getting_started/tools_and_agents.ipynb)

</div>

### Dive Deeper

<div class="grid cards" markdown>

-   :material-school:{ .lg .middle } __Learn__

    ---

    In-depth exploration of Mirascope's many features and capabilities

    [:octicons-arrow-right-24: Learn](./learn/index.md)

-   :material-book-open-variant:{ .lg .middle } __Tutorials__

    ---

    Advanced usage patterns and real-world applications

    [:octicons-arrow-right-24: Tutorials](./tutorials/more_advanced/text_classification.ipynb)

-   :material-connection:{ .lg .middle } __Integrations__

    ---

    Integrations with third-party tools for enhanced usage

    [:octicons-arrow-right-24: Integrations](./integrations/otel.md)

-   :material-text-search:{ .lg .middle } __API Reference__

    ---

    Detailed information on classes and functions

    [:octicons-arrow-right-24: Reference](./api/core/anthropic/call.md)

</div>

We're excited to see what you'll build with Mirascope, and we're here to help! Don't hesitate to reach out :)
