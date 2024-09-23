# Why Use Mirascope?

## Abstractions That Aren't Obstructions

Mirascope provides powerful abstractions that simplify LLM interactions without hiding the underlying mechanics. This approach gives you the convenience of high-level APIs while maintaining full control and transparency.

### Everything Beyond The Prompt Is Boilerplate

By eliminating boilerplate, Mirascope allows you to focus on what matter most: your prompt.

Let's compare structured outputs using Mirascope vs. the official OpenAI and Anthropic SDKs:

!!! mira "Mirascope"

    === "OpenAI"

        ```python
        --8<-- "examples/getting_started/why/boilerplate_reduction/openai/mirascope_call.py"
        ```

    === "Anthropic"

        ```python
        --8<-- "examples/getting_started/why/boilerplate_reduction/anthropic/mirascope_call.py"
        ```

!!! note "Official SDK"

    === "OpenAI"

        ```python
        --8<-- "examples/getting_started/why/boilerplate_reduction/openai/official_sdk_call.py"
        ```
   
    === "Anthropic"

        ```python
        --8<-- "examples/getting_started/why/boilerplate_reduction/anthropic/official_sdk_call.py"
        ```

Reducing this boilerplate becomes increasingly important as the number and complexity of your calls grows beyond a single basic example. Furthermore, the Mirascope interface works across all of our various supported providers, so you don't need to learn the intracacies of each provider to use them the same way.

### Functional, Modular Design

Mirascope's functional approach promotes modularity and reusability. You can easily compose and chain LLM calls, creating complex workflows with simple, readable code:

!!! mira ""

    === "Separate Calls"

        ```python hl_lines="6 12 16 22"
        --8<-- "examples/getting_started/why/modular_design/separate_calls.py"
        ```

    === "Nested Calls"

        ```python hl_lines="6 12 17"
        --8<-- "examples/getting_started/why/modular_design/nested_calls.py"
        ```

    === "Mixed Separate Calls"

        ```python hl_lines="7 17 21 27"
        --8<-- "examples/getting_started/why/modular_design/mixed_separate_calls.py"
        ```

    === "Mixed Nested Calls"

        ```python hl_lines="7 17 22"
        --8<-- "examples/getting_started/why/modular_design/mixed_nested_calls.py"
        ```

The goal of our design approach is to remain __Pythonic__ so you can __build your way__.

### Provider-Agnostic When Wanted, Specific When Needed

We understand the desire for easily switching between various LLM providers. We also understand the (common) need to engineer a prompt for a specific provider (and model).

By implementing our LLM API call functionality as decorators, Mirascope makes implementing any and all of these paths straightforward and easy:

!!! mira ""

    === "Provider-Specific"

        ```python hl_lines="6 12"
        --8<-- "examples/getting_started/why/provider_agnostic_specific/specific.py"
        ```

    === "Provider-Agnostic"

        ```python hl_lines="5 9 13"
        --8<-- "examples/getting_started/why/provider_agnostic_specific/agnostic.py"
        ```

### Type Hints & Editor Support

<div class="grid cards" markdown>

- :material-shield-check: __Type Safety__ to catch errors before runtime during lint
- :material-lightbulb-auto: __Editor Support__ for rich autocomplete and inline documentation

</div>

<video src="https://github.com/user-attachments/assets/174acc23-a026-4754-afd3-c4ca570a9dde" controls="controls" style="max-width: 730px;"></video>

## Who Should Use Mirascope?

Mirascope is __designed for everyone__ to use!

However, we believe that the value of Mirascope will shine in particular for:

- __Professional Developers__: Who need fine-grained control and transparency in their LLM interactions.
- __AI Application Builders__: Looking for a tool that can grow with their project from prototype to production.
- __Teams__: Who value clean, maintainable code and want to avoid the "black box" problem of many AI frameworks.
- __Researchers and Experimenters__: Who need the flexibility to quickly try out new ideas without fighting their tools.

## Getting Started

[:material-clock-fast: Getting Started](./index.md){: .md-button }
[:material-school: Learn](./learn/index.md){: .md-button }
[:material-account-group: Join Our Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA){: .md-button }

By choosing Mirascope, you're opting for a tool that respects your expertise as a developer while providing the conveniences you need to work efficiently and effectively with LLMs.

We believe the best tools get out of your way and let you focus on building great applications.
