# Why Use Mirascope?

Trusted by founders and engineers building the next generation of AI-native applications:

<div class="grid cards" markdown>

-   __Jake Duth__

    ---

    Co-Founder & CTO / Reddy

    ---

    "Mirascope's simplicity made it the natural next step from OpenAI's API — all without fighting the unnecessary complexity of tools like LangChain. We have all the bells and whistles we need for production while maintaining exceptional ease of use."

-   __Vince Trost__

    ---

    Co-Founder / Plastic Labs

    ---

    "The Pydantic inspired LLM toolkit the space has been missing. Simple, modular, extensible...helps where you need it, stays out of your way when you don't."

-   __Skylar Payne__

    ---

    VP of Engineering & DS / Health Rhythms

    ---

    "Mirascope's 'abstractions that aren't obstructions' tagline rings true – I was up and running in minutes, with seamless switching between AI providers. The type system catches any schema issues while I iterate, letting me focus entirely on crafting the perfect prompts."

-   __Off Sornsoontorn__

    ---

    Senior AI & ML Engineer / Six Atomic

    ---

    "LangChain required learning many concepts and its rigid abstractions made LLM behavior hard to customize. Mirascope lets us easily adapt LLM behaviors to any UI/UX design, so we can focus on innovation rather than working around limitations."

-   __William Profit__

    ---

    Co-Founder / Callisto

    ---

    "After trying many alternatives, we chose Mirascope for our large project and haven't looked back. It's simple, lean, and gets the job done without getting in the way. The team & community are super responsive, making building even easier."

-   __Rami Awar__

    ---

    Founder / DataLine

    ---

    "Migrating DataLine to Mirascope feels like I was rid of a pebble in my shoe that I never knew existed. This is what good design should feel like. Well done."

</div>

## Abstractions That Aren't Obstructions

Mirascope provides powerful abstractions that simplify LLM interactions without hiding the underlying mechanics. This approach gives you the convenience of high-level APIs while maintaining full control and transparency.

### Everything Beyond The Prompt Is Boilerplate

By eliminating boilerplate, Mirascope allows you to focus on what matter most: your prompt.

Let's compare structured outputs using Mirascope vs. the official SDKs:

!!! mira "Mirascope"

    {% for provider in supported_llm_providers %}
    === "{{ provider }}"

        ```python hl_lines="12 19"
        --8<-- "build/snippets/learn/response_models/basic_usage/{{ provider | provider_dir }}/shorthand.py:3:21"
        ```
    {% endfor %}

!!! note "Official SDK"

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
        {% elif provider == "Bedrock" %}
        ```python hl_lines="17-48 53"
        {% else %}
        ```python hl_lines="18-39 44"
        {% endif %}
        --8<-- "examples/learn/response_models/basic_usage/official_sdk/{{ provider | provider_dir }}_sdk.py"
        ```

    {% endfor %}

Reducing this boilerplate becomes increasingly important as the number and complexity of your calls grows beyond a single basic example. Furthermore, the Mirascope interface works across all of our various supported providers, so you don't need to learn the intracacies of each provider to use them the same way.

### Functional, Modular Design

Mirascope's functional approach promotes modularity and reusability. You can easily compose and chain LLM calls, creating complex workflows with simple, readable code:

!!! mira ""

    === "Separate Calls"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="6 11 14-15"
            {% elif method == "base_message_param" %}
            ```python hl_lines="5 10 19-20"
            {% else %}
            ```python hl_lines="5 10 14-15"
            {% endif %}
            --8<-- "build/snippets/learn/chaining/function_chaining/{{ provider | provider_dir }}/shorthand.py"
            ```
        {% endfor %}

    === "Nested Calls"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="6 10 12 15"
            {% elif method == "base_message_param" %}
            ```python hl_lines="5 11 15 20"
            {% else %}
            ```python hl_lines="5 11-12 15"
            {% endif %}
            --8<-- "build/snippets/learn/chaining/nested_chains/{{ provider | provider_dir }}/shorthand.py"
            ```
        {% endfor %}

The goal of our design approach is to remain __Pythonic__ so you can __build your way__.

### Provider-Agnostic When Wanted, Specific When Needed

We understand the desire for easily switching between various LLM providers. We also understand the (common) need to engineer a prompt for a specific provider (and model).

By implementing our LLM API call functionality as decorators, Mirascope makes implementing any and all of these paths straightforward and easy:

!!! mira ""

    === "Provider-Specific"

        ```python hl_lines="4-5 9-10 14 17"
        from mirascope.core import anthropic, openai


        @openai.call("gpt-4o-mini")
        def openai_recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"


        @anthropic.call("claude-3-5-sonnet-20240620")
        def anthropic_recommend_book(genre: str) -> str:
            return f"Recommend a {genre} book"


        openai_response = openai_recommend_book("fantasy")
        print(openai_response.content)

        anthropic_response = anthropic_recommend_book("fantasy")
        print(anthropic_response.content)
        ```

    === "Provider-Agnostic"

        ```python hl_lines="4-5 11-12 17-18"
        from mirascope.core import anthropic, openai, prompt_template


        @prompt_template()
        def recommend_book_prompt(genre: str) -> str:
            return f"Recommend a {genre} book"


        # OpenAI
        openai_model = "gpt-4o-mini"
        openai_recommend_book = openai.call(openai_model)(recommend_book_prompt)
        openai_response = openai_recommend_book("fantasy")
        print(openai_response.content)

        # Anthropic
        anthropic_model = "claude-3-5-sonnet-20240620"
        anthropic_recommend_book = anthropic.call(anthropic_model)(recommend_book_prompt)
        anthropic_response = anthropic_recommend_book("fantasy")
        print(anthropic_response.content)
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
