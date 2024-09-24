# Getting Started with Mirascope

<p align="left">
    <a href="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests"/></a>
    <a href="https://codecov.io/github/Mirascope/mirascope" target="_blank"><img src="https://codecov.io/github/Mirascope/mirascope/graph/badge.svg?token=HAEAWT3KC9" alt="Coverage"/></a>
    <a href="https://docs.mirascope.io/" target="_blank"><img src="https://img.shields.io/badge/docs-available-brightgreen" alt="Docs"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/v/mirascope.svg" alt="PyPI Version"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/pyversions/mirascope.svg" alt="Stars"/></a>
    <a href="https://github.com/Mirascope/mirascope/blob/dev/LICENSE"><img src="https://img.shields.io/github/license/Mirascope/mirascope.svg" alt="License"/></a>
</p>

LLM abstractions that aren't obstructions.

Mirascope is a powerful, flexible, and user-friendly library that simplifies the process of working with LLMs through a unified interface that works across various supported providers, including [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Mistral](https://mistral.ai/), [Gemini](https://gemini.google.com), [Groq](https://groq.com/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Vertex AI](https://cloud.google.com/vertex-ai).

Whether you're building chatbots, extracting structured information, or developing complex AI-driven agent systems, Mirascope provides the tools you need to streamline your development process and create powerful, robust applications.

!!! mira "Mirascope"

    === "OpenAI"

        ```python
        --8<-- "examples/getting_started/index/openai/mirascope_call.py"
        ```

    === "Anthropic"

        ```python
        --8<-- "examples/getting_started/index/anthropic/mirascope_call.py"
        ```

    === "Mistral"

        ```python
        --8<-- "examples/getting_started/index/mistral/mirascope_call.py"
        ```

    === "Gemini"

        ```python
        --8<-- "examples/getting_started/index/gemini/mirascope_call.py"
        ```

    === "Groq"

        ```python
        --8<-- "examples/getting_started/index/groq/mirascope_call.py"
        ```

    === "Cohere"

        ```python
        --8<-- "examples/getting_started/index/cohere/mirascope_call.py"
        ```

    === "LiteLLM"

        ```python
        --8<-- "examples/getting_started/index/litellm/mirascope_call.py"
        ```

    === "Azure AI"

        ```python
        --8<-- "examples/getting_started/index/azure/mirascope_call.py"
        ```
  
    === "Vertex AI"

        ```python
        --8<-- "examples/getting_started/index/vertex/mirascope_call.py"
        ```

!!! note "Official SDK"

    === "OpenAI"

        ```python
        --8<-- "examples/getting_started/index/openai/official_sdk_call.py"
        ```

    === "Anthropic"

        ```python
        --8<-- "examples/getting_started/index/anthropic/official_sdk_call.py"
        ```

    === "Mistral"

        ```python
        --8<-- "examples/getting_started/index/mistral/official_sdk_call.py"
        ```

    === "Gemini"

        ```python
        --8<-- "examples/getting_started/index/gemini/official_sdk_call.py"
        ```

    === "Groq"

        ```python
        --8<-- "examples/getting_started/index/groq/official_sdk_call.py"
        ```

    === "Cohere"

        ```python
        --8<-- "examples/getting_started/index/cohere/official_sdk_call.py"
        ```

    === "LiteLLM"

        ```python
        --8<-- "examples/getting_started/index/litellm/official_sdk_call.py"
        ```

    === "Azure AI"

        ```python
        --8<-- "examples/getting_started/index/azure/official_sdk_call.py"
        ```
    
    === "Vertex AI"

        ```python
        --8<-- "examples/getting_started/index/vertex/official_sdk_call.py"
        ```

## Installation

Install Mirascope, specifying the provider(s) you intend to use:

=== "OpenAI"

    ```bash
    pip install "mirascope[openai]"
    ```

=== "Anthropic"

    ```bash
    pip install "mirascope[anthropic]"
    ```

=== "Mistral"

    ```bash
    pip install "mirascope[mistral]"
    ```

=== "Gemini"

    ```bash
    pip install "mirascope[gemini]"
    ```

=== "Groq"

    ```bash
    pip install "mirascope[groq]"
    ```

=== "Cohere"

    ```bash
    pip install "mirascope[cohere]"
    ```

=== "LiteLLM"

    ```bash
    pip install "mirascope[litellm]"
    ```

=== "Azure AI"

    ```bash
    pip install "mirascope[azure]"
    ```

=== "Vertex AI"

    ```bash
    pip install "mirascope[vertex]"
    ```

Set up your API key:

=== "OpenAI"

    ```python
    import os

    os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
    ```

=== "Anthropic"

    ```python
    import os

    os.environ["ANTHROPIC_API_KEY"] = "YOUR_API_KEY"
    ```

=== "Mistral"

    ```python
    import os

    os.environ["MISTRAL_API_KEY"] = "YOUR_API_KEY"
    ```

=== "Gemini"

    ```python
    import os

    os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
    ```

=== "Groq"

    ```python
    import os

    os.environ["GROQ_API_KEY"] = "YOUR_API_KEY"
    ```

=== "Cohere"

    ```python
    import os

    os.environ["CO_API_KEY"] = "YOUR_API_KEY"
    ```

=== "LiteLLM"

    ```python
    import os

    os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"  # set keys for providers you will use
    ```

=== "Azure AI"

    ```python
    import os

    os.environ["AZURE_INFERENCE_ENDPOINT"] = "YOUR_ENDPOINT"
    os.environ["AZURE_INFERENCE_CREDENTIAL"] = "YOUR_CREDENTIAL"
    ```

=== "Vertex AI"

    ```python
    import vertexai

    vertexai.init(...)  # provide necessary settings/credentials
    ```

## Choose Your Path

### Getting Started Notebooks

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Quickstart Guide__

    ---

    Comprehensive overview of core features and building blocks

    [:octicons-arrow-right-24: Quickstart](https://github.com/Mirascope/mirascope/blob/dev/examples/getting_started/notebooks/quickstart.ipynb)

-   :material-database:{ .lg .middle } __Structured Outputs__

    ---

    Explore various techniques for generating structured outputs

    [:octicons-arrow-right-24: Structured Outputs](https://github.com/Mirascope/mirascope/blob/dev/examples/getting_started/notebooks/structured_outputs.ipynb)

-   :material-link-variant:{ .lg .middle } __Dynamic Configuration & Chaining__

    ---

    Examples ranging from basic usage to more complex chaining techniques

    [:octicons-arrow-right-24: Dynamic Configuration & Chaining](https://github.com/Mirascope/mirascope/blob/dev/examples/getting_started/notebooks/dynamic_config_and_chaining.ipynb)

-   :material-tools:{ .lg .middle } __Tools & Agents__

    ---

    Learn how to define tools for your LLM to build advanced AI agents

    [:octicons-arrow-right-24: Tools & Agents](https://github.com/Mirascope/mirascope/blob/dev/examples/getting_started/notebooks/tools_and_agents.ipynb)

</div>

### Dive Deeper

<div class="grid cards" markdown>

-   :material-school:{ .lg .middle } __Learn__

    ---

    In-depth exploration of Mirascope's many features and capabilities

    [:octicons-arrow-right-24: Learn](./learn/index.md)

-   :material-book-open-variant:{ .lg .middle } __Cookbook__

    ---

    Advanced usage patterns and real-world applications

    [:octicons-arrow-right-24: Cookbook](./cookbook/index.md)

-   :material-text-search:{ .lg .middle } __API Reference__

    ---

    Detailed information on classes and functions

    [:octicons-arrow-right-24: Reference](./api/index.md)

-   :material-connection:{ .lg .middle } __Integrations__

    ---

    Integrations with third-party tools for enhanced usage

    [:octicons-arrow-right-24: Integrations](./integrations/index.md)

</div>

## Key Features

- [Prompt Templates](./learn/prompts.md): Dynamic prompt creation with type-safe templating
- [LLM Calls](./learn/calls.md): Simplified API interactions across multiple providers
- [Streaming](./learn/streams.md): Real-time responses for improved user experience
- [Response Models](./learn/response_models.md): Easily extract and validate structured information with Pydantic
- [Custom Tools](./learn/tools.md): Extend LLM capabilities with your own functions
- [Agents](./learn/tools.md): Effortlessly manage state and integrate custom tools

## Next Steps

[:material-lightbulb: Why Use Mirascope](./WHY.md){: .md-button }
[:material-account-group: Join Our Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA){: .md-button }
[:material-star: Star the Repo](https://github.com/Mirascope/mirascope){: .md-button }  

We're excited to see what you'll build with Mirascope, and we're here to help! Don't hesitate to reach out :)
