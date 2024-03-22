"""A basic prompt to solve a math problem."""

from mirascope import tags
from mirascope.openai import OpenAICall

prev_revision_id = "0001"
revision_id = "0002"


@tags(["version:0002"])
class ProblemSolver(OpenAICall):
    prompt_template = """
    Here is a math problem: {problem}
    Write out the answer step by step to arrive at the conclusion.
    """

    problem: str
