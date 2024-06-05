import os

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class ScientistSelector(OpenAICall):
    prompt_template = """
    Name a scientist who is well-known for their work in {field_of_study}.
    Give me just the name.
    """

    field_of_study: str


class TheoryExplainer(OpenAICall):
    prompt_template = """
    SYSTEM:
    Imagine that you are scientist {scientist}.
    Your task is to explain a theory that you, {scientist}, are famous for.

    USER:
    Explain the theory of {theory}.
    """

    scientist: str
    theory: str


selector = ScientistSelector(field_of_study="physics")
scientist = selector.call().content
print(scientist)
# > Albert Einstein.

explainer = TheoryExplainer(scientist=scientist, theory="relativity")
theory_explanation = explainer.call().content
print(theory_explanation)
# > Certainly! Here's an explanation of the theory of relativity: ...
