# Code Generation and Execution

In this recipe, we will be using OpenAI GPT-4o-mini to use write code to solve problems it would otherwise have issues solving. 

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Models](../learn/response_models.md)
    - [Agents](../learn/agents.md)

## Create your agent

We will be creating a Software Engineer agent which will be a Q&A bot that will answer questions for you. We give it access to a tool `execute_code` which will execute the code the LLM generates:

```python
--8<-- "examples/cookbook/code_generation_and_execution.py:3:4"
--8<-- "examples/cookbook/code_generation_and_execution.py:20:"
```

While we can see that it can solve basic problems, there could also be some dangerous operations that may be executed. Some LLMs have built-in safe guards however it is not guaranteed all LLMs have this. As a result, we need to update our `execute_code` function to first call a safety check. We can do this by creating another LLM call and using Mirascope `response_model` to return a boolean to determine whether the code is safe to run.

## Add safety

```python
--8<-- "examples/cookbook/code_generation_and_execution.py:6:32"
```

Let's take a look at the following user request with code safety enabled:

```python
--8<-- "examples/cookbook/code_generation_and_execution.py:90:"
# Output:
"""
(User): Can you list my current directory
(Assistant): I cannot execute code that interacts with the filesystem for safety reasons. However, I can provide you with the code that you can run in your local environment to list the current directory:
# 
```python
import os
# 
result = os.listdir('.')
print(result)
"""
```

Without code safety:

```python
--8<-- "examples/cookbook/code_generation_and_execution.py:90:"
# Output:
"""
(User): Can you list my current directory
(Assistant): The contents of your current directory are as follows:

- foo.py
- bar.py
- baz.txt
"""
```

Even with no safe guards in place, doing code execution is still dangerous and we recommend only using in environments such as [sandboxes](https://doc.pypy.org/en/latest/sandbox.html).

!!! tip "Additional Real-World Applications"

- **Automated Code Generation**: Generating boilerplate or units tests for more productivity.
- **Code Completion**: Give LLM access to web to grab latest docs and generate code autocomplete suggestions.
- **Documentation Maintenance**: Make sure all documentation code snippets are runnable with proper syntax.
- **Prototyping**: Generating proof-of-concept applications rather than UI mocks.

When adapting this recipe to your specific use-case, consider the following:

- Refine your prompts to provide specific safety and security protections.
- Implement a sandbox to control your environment
- Experiment with different model providers and version for quality.
