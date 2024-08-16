from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, SkipValidation

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", response_model=bool)
@prompt_template(
    """
    SYSTEM:
    You are a software engineer who is an expert at reviewing whether code is safe to execute.
    Determine if the given string is safe to execute as Python code.

    USER:
    {code}
    """
)
def evaluate_code_safety(code: str): ...


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


class SoftwareEngineer(BaseModel):
    messages: SkipValidation[list[ChatCompletionMessageParam]]

    @openai.call(model="gpt-4o-mini", tools=[execute_code])
    @prompt_template(
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
    )
    def _step(self, text: str): ...

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
