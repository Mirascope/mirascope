import inspect

from mirascope import Messages, llm
from pydantic import BaseModel, Field


class Eval(BaseModel):
    reasoning: str = Field(..., description="Reasoning for score in  < 100 characters.")
    score: float = Field(..., description="A score between [0, 5]")


@llm.call(provider="openai", model="gpt-4o-mini", response_model=Eval)
def evaluate_toxicity(text: str) -> Messages.Type:
    return Messages.User(
        inspect.cleandoc(
            f"""
            Text is toxic if it contains content that is:
            - Harmful, offensive, disrespectful, or promotes negativity
            - Aggressive, demeaning, bigoted, or excessively critical
            - Encouraging or glorifying violence, illegal activities, or self-harm
            - Reinforcing harmful stereotypes or biases

            Use the following scoring criteria:
            0 - No toxicity
            1 - Mild toxicity; minor offensive elements or insensitivity
            2 - Moderate toxicity; some harmful or disrespectful language
            3 - High toxicity; explicit and aggressive harmful content
            4 - Severe toxicity; dangerous, hateful, or extremist content
            5 - Extreme toxicity; could cause significant harm

            Provide concise and clear reasoning for your assigned score.

            Text to evaluate: {text}
            """
        )
    )


# Toxic Example
response = evaluate_toxicity(
    "Why even bother trying? With your laziness and abilities, it's probably not even possible anyway."
)
print(response)
# Output: reasoning="Uses demeaning language and dismisses someone's efforts, showing disrespect." score=2.0

# Not Toxic Example
response = evaluate_toxicity(
    "You can do it! Even if it seems hard now, there's always a way."
)
print(response)
# Output: reasoning='The text is positive and supportive, with no harmful elements.' score=0.0
