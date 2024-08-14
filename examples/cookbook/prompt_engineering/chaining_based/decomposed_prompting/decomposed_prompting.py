import json

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


class Problem(BaseModel):
    subproblems: list[str] = Field(
        ..., description="The subproblems that the original problem breaks down into"
    )


@openai.call(model="gpt-4o-mini", response_model=Problem)
@prompt_template(
    """
    Your job is to break a problem into subproblems so that it may be solved
    step by step, using at most one function call at each step.

    You have access to the following functions which you can use to solve a
    problem:
    split: split a string into individual words
    substring: get the ith character of a single string.
    concat: concatenate some number of strings.

    Here is an example of how it would be done for the problem: Get the first two
    letters of the phrase 'Round Robin' with a period and space in between them.
    Steps:
    split 'Round Robin' into individual words
    substring the 0th char of 'Round'
    substring the 0th char of 'Robin'
    concat ['R', '.', ' ', 'R']

    Now, turn this problem into subtasks:
    {query}
    """
)
def break_into_subproblems(query: str): ...


def split(str: str) -> str:
    """Splits a string into words."""
    return json.dumps(str.split())


def substring(index: int, str: str) -> str:
    """Gets the character at the index of a string."""
    return str[index]


def concat(strings: list[str]) -> str:
    """Concatenates some number of strings."""
    return "".join(strings)


@openai.call(model="gpt-3.5-turbo", tools=[split, substring, concat])
@prompt_template(
    """
    SYSTEM: You are being fed subproblems to solve the actual problem: {query}
    MESSAGES: {history}
    """
)
def solve_next_step(history: list[ChatCompletionMessageParam], query: str): ...


def decomposed_prompting(query: str):
    problem = break_into_subproblems(query=query)
    # Uncomment to see intermediate responses
    # print(problem.subproblems)
    response = None
    history: list[ChatCompletionMessageParam] = []
    for subproblem in problem.subproblems:
        history.append({"role": "user", "content": subproblem})
        response = solve_next_step(history, query)
        # print(response)
        history.append(response.message_param)
        if tool := response.tool:
            output = tool.call()
            history += response.tool_message_params([(tool, output)])
            response = solve_next_step(history, query)
            # print(response)
            history.append(response.message_param)
    return response


query = """Take the last letters of the words in ”Augusta Ada King” and concatenate
them using a space."""


print(decomposed_prompting(query))
# > The concatenated string is "a a g".


# Intermediate Responses

# problem = break_into_subproblems(prompt)
# problem.subproblems
# > ["split 'Augusta Ada King' into individual words", "substring the last character of 'Augusta'", "substring the last character of 'Ada'", "substring the last character of 'King'", "concat ['a', ' ', 'a', ' ', 'g']"]

# response = solve_next_step(history, query)
# > The words in "Augusta Ada King" are ["Augusta", "Ada", "King"].
# > The last character of "Augusta" is 'a'.
# > The last character of "Ada" is 'a'.
# > The last character of "King" is 'g'.
# > The concatenated string is "a a g".
