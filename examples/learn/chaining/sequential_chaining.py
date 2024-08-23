from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Name a scientist who is well-known for their work in {field_of_study}.
    Give me just the name.
    """
)
def scientist_selector(field_of_study: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Imagine that you are scientist {scientist}.
    Your task is to explain a theory that you, {scientist}, are famous for.
    """
)
def theory_explainer(scientist: str, theory: str): ...


scientist = scientist_selector(field_of_study="physics").content
print(scientist)
# > Albert Einstein.

theory_explanation = theory_explainer(scientist=scientist, theory="relativity").content
print(theory_explanation)
# > Certainly! Here's an explanation of the theory of relativity: ...
