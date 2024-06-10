"""How to use python properties with Mirascope"""
from mirascope import BasePrompt

# Alternatively use cached_property on computationally expensive operations
# from functools import cached_property


class AdditionCalculator(BasePrompt):
    prompt_template = """
    Can you solve this math problem for me?
    {addition_equation}
    """
    first_number: float
    second_number: float

    @property
    def addition_equation(self) -> str:
        return f"{self.first_number}+{self.second_number}="


addition_calculator = AdditionCalculator(first_number=6, second_number=10)
print(addition_calculator.addition_equation)
# > 6.0+10.0=
print(addition_calculator)
# > Can you solve this math problem for me?
#   6.0+10.0=
print(addition_calculator.dump())
# Note that addition_equation does not show up in inputs.
# See examples/writing_prompts/using_computed_fields.py
# > {
#        "tags": [],
#        "template": "Can you solve this math problem for me?\n{addition_equation}",
#        "inputs": {"first_number": 6.0, "second_number": 10.0},
#   }
