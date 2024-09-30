# Generate SQL with LLM

In this recipe, we will be using OpenAI GPT-4o-mini to act as a co-pilot for a Database Admin. While LLMs are powerful and do pretty well at transforming laymen queries into SQL queries, it is still dangerous to do so without supervision. This recipe will have no guardrails for mutable operations and is purely for getting started.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Tools](../../learn/tools.md)
    - [Async](../../learn/async.md)
    - [Agents](../../learn/agents.md)

## Setup

We will be using SQLite, but this example will work for any common SQL dialect, such as PostgreSQL, MySQL, MSSQL, and more.

```bash
pip install sqlite3
```

## Setup SQL Database

Replace this part with whichever SQL dialect you are using, or skip if you have a database set up already.

```python
--8<-- "examples/cookbook/agents/sql_agent/setup_without_sql_file.py"
```

This will be our playground example.

## Write your Database Assistant

We will be creating an Agent that will take non-technical queries and translate them into SQL queries that will be executed. The first step will be to create our two tools, `_run_query` and `_execute_query` , which will be read and write operations respectively.

```python
--8<-- "examples/cookbook/agents/sql_agent/agent.py:2:6"
--8<-- "examples/cookbook/agents/sql_agent/agent.py:8:41"
```

Now that we have our tools setup it is time to engineer our prompt

## Prompt Engineering

Knowing what tools are available is crucial when prompt engineering, so that we can tell the LLM when and how the tools should be used.

Now we will take our `Librarian` and add our `@openai.call`:

```python
--8<-- "examples/cookbook/agents/sql_agent/agent.py:7:15"
    ...
--8<-- "examples/cookbook/agents/sql_agent/agent.py:42:128"
```

Let's break down the prompt:

1. We give the LLM a friendly personality, which is an optional but crucial feature for user-facing applications.
2. We provide the LLM with knowledge of the database schema that it will operate on.
3. We give example interactions to reinforce how the LLM should operate.
4. We give more fine-tuned instructions and constraints
5. We tell the LLM how to use its tools

After writing our prompt, we go through our agent loop and we can now use our Librarian.

```python
--8<-- "examples/cookbook/agents/sql_agent/agent.py:1:1"
--8<-- "examples/cookbook/agents/sql_agent/agent.py:129:148"
```

Note that the SQL statements in the dialogue are there for development purposes.

Having established that we can have a quality conversation with our `Librarian`, we can now enhance our prompt. However, we must ensure that these improvements don't compromise the Librarian's core functionality. Check out [Evaluating SQL Agent](../evals/evaluating_sql_agent.ipynb) for an in-depth guide on how we evaluate the quality of our prompt.



!!! tip "Additional Real-World Examples"
    - **Operations Assistant**: A read-only agent that retrieves data from databases, requiring no technical expertise.
    - **SQL Query Optimization**: Provide the agent with your data retrieval goals, and have it generate an efficient SQL query to meet your needs.
    - **Data Generation for Testing**: Request the agent to create and populate your database with realistic sample data to support development and testing processes.

When adapting this recipe to your specific use-case, consider the following:

- Experiment with the prompt, by adding query planning or other prompting techniques to break down a complex request.
- Experiment with different model providers to balance quality and speed.
- Use in a development or sandbox environment for rapid development.
