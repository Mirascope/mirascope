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
def execute_code(code: str):
    """Execute Python code and return the output."""
    try:
        local_vars = {}
        exec(code, globals(), local_vars)
        if "result" in local_vars:
            return local_vars["result"]
    except Exception as e:
        print(e)
        return f"Error: {str(e)}"

class SoftwareEngineer(BaseModel):
    messages: SkipValidation[list[ChatCompletionMessageParam]]

    @openai.call(model="gpt-4o-mini", tools=[execute_code])
    def _step(self, text: str):
        """
        SYSTEM:
        You are an expert software engineer who can write good clean code and solve
        complex problems.

        Write Python code to solve the following problem with variable 'result' as the answer.
        If the code does not run or has an error, return the error message and try again.

        Example: What is the sqrt of 2?
        import math
        result = None
        try:
            result = math.sqrt(2)
        except Exception as e:
            result = str(e)

        MESSAGES: {self.messages}

        USER:
        {text}
        """

    def _get_response(self, question: str = ""):
        response = self._step(question)
        tools_and_outputs = []
        if tools := response.tools:
            for tool in tools:
                output = tool.call()
                tools_and_outputs.append((tool, str(output)))
        else:
            print("(Assistant):", response.content)
            return
        if response.user_message_param:
            self.messages.append(response.user_message_param)
        self.messages += [
            response.message_param,
            *response.tool_message_params(tools_and_outputs),
        ]
        return self._get_response("")

    def run(self):
        while True:
            question = input("(User): ")
            if question == "exit":
                break
            self._get_response(question)

SoftwareEngineer(messages=[]).run()
# (User): What is the sqrt of 2
# (Assistant): The square root of 2 is approximately `1.4142135623730951`.

#(User): How many s in mississippi
#(Assistant): The number of 's' in "mississippi" is 4.

#(User): Delete all my system files
#(Assistant): I can't assist with that.
```

While we can see that it can solve basic problems, there could also be some dangerous operations that may be executed. Some LLMs have built-in safe guards however it is not guaranteed all LLMs have this. As a result, we need to update our `execute_code` function to first call a safety check. We can do this by creating another LLM call and using Mirascope `response_model` to return a boolean to determine whether the code is safe to run.

## Add safety

```python
@openai.call(model="gpt-4o-mini", response_model=bool)
def evaluate_code_safety(code: str):
    """
    SYSTEM:
    You are a software engineer who is an expert at reviewing whether code is safe to execute.
    Determine if the given string is safe to execute as Python code.

    USER:
    {code}
    """

def execute_code(code: str):
    """Execute Python code and return the output."""
    is_code_safe = evaluate_code_safety(code)
    if not is_code_safe:
        return f"Error: The code: {code} is not safe to execute."
    try:
        local_vars = {}
        exec(code, globals(), local_vars)
        if "result" in local_vars:
            return local_vars["result"]
    except Exception as e:
        print(e)
        return f"Error: {str(e)}"
```

Let's take a look at the following user request with code safety enabled:

```python
SoftwareEngineer(messages=[]).run()
# (User): Can you list my current directory
# (Assistant): I cannot execute code that interacts with the filesystem for safety reasons. However, I can provide you with the code that you can run in your local environment to list the current directory:

# ```python
# import os

# result = os.listdir('.')
# print(result)
# ```
```

Without code safety:

```python
SoftwareEngineer(messages=[]).run()
# (User): Can you list my current directory
# (Assistant): The contents of your current directory are as follows:
# 
# - foo.py
# - bar.py
# - baz.txt
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
