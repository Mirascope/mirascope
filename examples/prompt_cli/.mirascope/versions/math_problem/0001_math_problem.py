"""A basic prompt to solve a math problem."""

from mirascope import tags
from mirascope.openai import OpenAICall

prev_revision_id = None
revision_id = "0001"


@tags(["version:0001"])
class ProblemSolver(OpenAICall):
    prompt_template = """
    Here is a math problem: {problem}
    Give me just the answer as one number.
    """

    problem: str
