"""How to use Pydantic computed_field with Mirascope"""
from pydantic import computed_field

from mirascope import BasePrompt


class AdditionCalculator(BasePrompt):
    prompt_template = """
    Can you solve this math problem for me?
    {addition_equation}
    """
    first_number: float
    second_number: float

    @computed_field
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
# > {
#        "tags": [],
#        "template": "Can you solve this math problem for me?\n{addition_equation}",
#        "inputs": {
#            "first_number": 6.0,
#            "second_number": 10.0,
#            "addition_equation": "6.0+10.0=",
#        }
#   }
