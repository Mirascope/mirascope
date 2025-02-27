---
search:
  boost: 2
---

# Agents

> __Definition__: a person who acts on behalf of another person or group

When working with Large Language Models (LLMs), an "agent" refers to an autonomous or semi-autonomous system that can act on your behalf. The core concept is the use of tools to enable the LLM to interact with its environment.

In this section we will implement a toy `Librarian` agent to demonstrate key concepts in Mirascope that will help you build agents.

!!! mira ""

    <div align="center">
        If you haven't already, we recommend first reading the section on [Tools](./tools.md)
    </div>

??? info "Diagram illustrating the agent flow"

    ```mermaid
    sequenceDiagram
        participant YC as Your Code
        participant LLM

        loop Agent Loop
            YC->>LLM: Call with prompt + history + function definitions
            loop Tool Calling Cycle
                LLM->>LLM: Decide to respond or call functions
                LLM->>YC: Respond with function to call and arguments
                YC->>YC: Execute function with given arguments
                YC->>YC: Add tool call message parameters to history
                YC->>LLM: Call with prompt + history including function result
            end
            LLM->>YC: Finish calling tools and return final response
            YC->>YC: Update history with final response
        end
    ```

## State Management

Since an agent needs to operate across multiple LLM API calls, the first concept to cover is state. The goal of providing state to the agent is to give it memory. For example, we can think of local variables as "working memory" and a database as "long-term memory".

Let's take a look at a basic chatbot (not an agent) that uses a class to maintain the chat's history:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="6 12 26-29"
            {% else %}
            ```python hl_lines="6 12 24-27"
            {% endif %}
            --8<-- "build/snippets/learn/agents/state_management/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}
    {% endfor %}

In this example we:

- Create a `Librarian` class with a `history` attribute.
- Implement a private `_call` method that injects `history`.
- Run the `_call` method in a loop, saving the history at each step.

A chatbot with memory, while more advanced, is still not an agent.

??? tip "Provider-Agnostic Agent"

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% if method == "string_template" %}
        ```python hl_lines="20-21 28"
        {% else %}
        ```python hl_lines="18-19 26"
        {% endif %}
        --8<-- "examples/learn/agents/state_management/provider_agnostic/{{ method }}.py"
        ```

    {% endfor %}

## Integrating Tools

The next concept to cover is introducing tools to our chatbot, turning it into an agent capable of acting on our behalf. The most basic agent flow is to call tools on behalf of the agent, providing them back through the chat history until the agent is ready to response to the initial query.

Let's take a look at a basic example where the `Librarian` can access the books available in the library:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="19-23 25-27 38 45-51"
            {% else %}
            ```python hl_lines="14-17 19-21 30 37-43"
            {% endif %}
            --8<-- "build/snippets/learn/agents/tools/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}
    {% endfor %}

In this example we:

1. Added the `library` state to maintain the list of available books.
2. Implemented the `_available_books` tool that returns the library as a string.
3. Updated `_call` to give the LLM access to the tool.
    - We used the `tools` dynamic configuration field so the tool has access to the library through `self`.
4. Added a `_step` method that implements a full step from user input to assistant output.
5. For each step, we call the LLM and see if there are any tool calls.
    - If yes, we call the tools, collect the outputs, and insert the tool calls into the chat history. We then recursively call `_step` again with an empty user query until the LLM is done calling tools and is ready to response
    - If no, the LLM is ready to respond and we return the response content.

Now that our chatbot is capable of using tools, we have a basic agent.

## Human-In-The-Loop

While it would be nice to have fully autonomous agents, LLMs are far from perfect and often need assistance to ensure they continue down the right path in an agent flow.

One common and easy way to help guide LLM agents is to give the agent the ability to ask for help. This "human-in-the-loop" flow lets the agent ask for help if it determines it needs it:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="14-20 31"
            {% else %}
            ```python hl_lines="8-14 23"
            {% endif %}
            --8<-- "build/snippets/learn/agents/human_in_the_loop/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}
    {% endfor %}

## Streaming

The previous examples print each tool call so you can see what the agent is doing before the final response; however, you still need to wait for the agent to generate its entire final response before you see the output.

Streaming can help to provide an even more real-time experience:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            {% if method == "string_template" %}
            ```python hl_lines="29 37 43-54"
            {% else %}
            ```python hl_lines="23 24 35-46"
            {% endif %}
            --8<-- "build/snippets/learn/agents/streaming/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}
    {% endfor %}

## Next Steps

This section is just the tip of the iceberg when it comes to building agents, implementing just one type of simple agent flow. It's important to remember that "agent" is quite a general term and can mean different things for different use-cases. Mirascope's various features make building agents easier, but it will be up to you to determine the architecture that best suits your goals.

Next, we recommend taking a look at our [Agent Tutorials](../tutorials/agents/web_search_agent.ipynb) to see examples of more complex, real-world agents.
