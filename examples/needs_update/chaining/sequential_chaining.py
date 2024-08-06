"""Simple chaining by passing the result of one function to the next."""

import os

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai.call(model="gpt-3.5-turbo")
def scientist_selector(field_of_study: str):
    """
    Name a scientist who is well-known for their work in {field_of_study}.
    Give me just the name.
    """


@openai.call(model="gpt-3.5-turbo")
def theory_explainer(scientist: str, theory: str):
    """
    Imagine that you are scientist {scientist}.
    Your task is to explain a theory that you, {scientist}, are famous for.
    """


scientist = scientist_selector(field_of_study="physics").content
print(scientist)
# > Albert Einstein.

theory_explanation = theory_explainer(scientist=scientist, theory="relativity").content
print(theory_explanation)
# > Certainly! Here's an explanation of the theory of relativity: ...
