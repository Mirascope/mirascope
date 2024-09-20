# Query Plan

This recipe shows how to use LLMs — in this case, Anthropic’s Claude 3.5 Sonnet — to create a query plan. Using a query plan is a great way to get more accurate results by breaking down a complex question into multiple smaller questions.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Tools](../learn/tools.md)
    - [Dynamic Configuration](../learn/dynamic_configuration.md)
    - [Chaining](../learn/chaining.md)
    - [JSON Mode](../learn/json_mode.md)
    - [Response Models](../learn/response_models.md)

## Create your Query

To construct our Query Plan, we first need to define the individual queries that will comprise it using a Pydantic BaseModel:

```python
--8<-- "examples/cookbook/query_plan.py:5:6"
--8<-- "examples/cookbook/query_plan.py:11:23"
```

Each query is assigned a unique ID, which can reference other queries for dependencies. We also provide necessary tools and the relevant portion of the broken-down question to each query.

## Create our tool

For the purposes of this recipe, we will define some dummy data. This tool should be replaced by web_search, a database query, or other forms of pulling data.

```python
--8<-- "examples/cookbook/query_plan.py:1:2"
--8<-- "examples/cookbook/query_plan.py:45:92"
```

## Define our Query Planner

Let us prompt our LLM call to create a query plan for a particular question:

```python
--8<-- "examples/cookbook/query_plan.py:7:8"
--8<-- "examples/cookbook/query_plan.py:26:42"
```

We set the `response_model` to the `Query` object we just defined. We also prompt the call to add tools as necessary to the individual `Query`. Now we make a call to the LLM:

```python
--8<-- "examples/cookbook/query_plan.py:128:158"
```

We can see our `list[Query]` and their respective subquestions and tools needed to answer the main question. We can also see that the final question depends on the answers from the previous queries.

## Executing our Query Plan

Now that we have our list of queries, we can iterate on each of the subqueries to answer our main question:

```python
--8<-- "examples/cookbook/query_plan.py:3:3"
--8<-- "examples/cookbook/query_plan.py:93:125"
```

Using Mirascope’s `DynamicConfig` , we can pass in the tools from the query plan into our LLM call. We also add history to the calls that have dependencies.

Now we run `execute_query_plan`:

```python
--8<-- "examples/cookbook/query_plan.py:159:191"
```

!!! tip "Additional Real-World Examples"

    - **Enhanced ChatBot**: Provide higher quality and more accurate answers by using a query plan to answer complex questions.
    - **Database Administrator**: Translate layperson requests into a query plan, then execute SQL commands to efficiently retrieve or manipulate data, fulfilling the user's requirements.
    - **Customer support**: Take a user request and turn it into a query plan for easy to follow and simple instructions for troubleshooting.

When adapting this recipe to your specific use-case, consider the following:

    - Agentic: Turn this example into a more flexible Agent which has access to a query plan tool.
    - Multiple providers: Use multiple LLM providers to verify whether the extracted information is accurate and not hallucination.
    - Implement Pydantic `ValidationError` and Tenacity `retry` to improve reliability and accuracy.
