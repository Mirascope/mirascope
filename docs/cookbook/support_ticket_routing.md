# Support Ticket Routing

This recipe shows how to take an incoming support ticket/call transcript then use an LLM to summarize the issue and route it to the correct person.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Tools](../learn/tools.md)
    - [Chaining](../learn/chaining.md)
    - [Response Models](../learn/response_models.md)

!!! note "Background"

    Traditional machine learning techniques like text classification were previously used to solve routing. LLMs have enhanced routing by being able to better interpret nuances of inquiries as well as using client history and knowledge of the product to make more informed decisions.

## Imitating a Company’s Database/Functionality

!!! note "Fake Data"

    For both privacy and functionality purposes, these data types and functions in *no way* represent how a company’s API should actually look like. However, extrapolate on these gross oversimplifications to see how the LLM would interact with the company’s API.

### User

Let’s create a `User` class to represent a customer as well as the function `get_user_by_email()` to imitate how one might search for the user in the database with some identifying information:

```python
--8<-- "examples/cookbook/support_ticket_routing.py:3:4"
--8<-- "examples/cookbook/support_ticket_routing.py:7:32"
```

### Data Pulling Functions

Let’s also define some basic functions that one might expect a company to have for specific situations. `get_sale_items()` gets the items currently on sale, `get_rewards()` gets the rewards currently available to a user, `get_billing_details()` returns user data related to billing, and `get_account_details()` returns user data related to their account.

```python
--8<-- "examples/cookbook/support_ticket_routing.py:35:62"
```

### Routing to Agent

Since we don’t have an actual endpoint to route to a live agent, let’s use this function `route_to_agent()` as a placeholder:

```python
--8<-- "examples/cookbook/support_ticket_routing.py:1:2"
--8<-- "examples/cookbook/support_ticket_routing.py:65:69"
```

## Handling the Ticket

To handle the ticket, we will classify the issue of the ticket in one call, then use the classification to gather the corresponding context for a second call.

### Classify the Transcript

Assume we have a basic transcript from the customer’s initial interactions with a support bot where they give some identifying information and their issue. We define a Pydantic `BaseModel` schema to classify the issue as well as grab the identifying information. `calltype` classifies the transcript into one of the three categories `billing`, `sale`, and `support`, and `user_email` will grab their email, assuming that’s what the bot asks for. The `reasoning` field will not be used, but forcing the LLM to give a reasoning for its classification choice aids in extraction accuracy, which can be shaky:

```python
--8<-- "examples/cookbook/support_ticket_routing.py:3:4"
--8<-- "examples/cookbook/support_ticket_routing.py:71:85"
```

And we can extract information into this schema with the call `classify_transcript()`:

```python
--8<-- "examples/cookbook/support_ticket_routing.py:5:7"
--8<-- "examples/cookbook/support_ticket_routing.py:88:95"
```

### Provide Ticket-Specific Context

Now, depending on the output of `classify_transcript()`, we would want to provide different context to the next call - namely, a `billing` ticket would necessitate the details from `get_billing_details()`, a `sale` ticket would want the output of `get_sale_items()` and `get_rewards()`, and a `support_ticket` would require `get_account_details`. We define a second call `handle_ticket()` which calls `classify_transcript()` and calls the correct functions for the scenario via dynamic configuration:

```python
--8<-- "examples/cookbook/support_ticket_routing.py:98:126"
```

And there you have it! Let’s see how `handle_ticket` deals with each of the following transcripts:

```python
--8<-- "examples/cookbook/support_ticket_routing.py:129:167"
```

!!! tip "Additional Real-World Examples"

    - **IT Help Desk**: Have LLM determine whether the user request is level 1, 2, or 3 support and route accordingly
    - **Software-as-a-Service (SaaS) Companies**: A question about how to use a specific feature might be routed to the product support team, while an issue with account access could be sent to the account management team.

When adapting this recipe to your specific use-case, consider the following:

    - Update the `response_model` to more accurately reflect your use-case.
    - Implement Pydantic `ValidationError` and Tenacity `retry` to improve reliability and accuracy.
    - Evaluate the quality of extraction by using another LLM to verify classification accuracy.
    - Use a local model like Ollama to protect company or other sensitive data.
