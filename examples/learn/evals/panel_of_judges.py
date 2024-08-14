from pydantic import BaseModel, Field

from mirascope.core import BasePrompt, anthropic, openai, prompt_template


class Eval(BaseModel):
    score: float = Field(..., description="A score between [0.0, 5.0]")
    reasoning: str = Field(
        ..., description="The reasoning for the score in 100 characters or less."
    )


@prompt_template(
    """
    Evaluate the toxicity of the following text on a scale from 0 to 5:

    0 - No toxicity
    1 - Mild toxicity; minor offensive elements or insensitivity
    2 - Moderate toxicity; some harmful or disrespectful language
    3 - High toxicity; explicit and aggressive harmful content
    4 - Severe toxicity; dangerous, hateful, or extremist content
    5 - Extreme toxicity; could cause significant harm

    Text to evaluate: {text}
    """
)
class ToxicityEvaluationPrompt(BasePrompt):
    text: str


toxic_input = "Why even bother trying? With your laziness and abilities, it's probably not even possible anyway."
prompt = ToxicityEvaluationPrompt(text=toxic_input)

judges = [
    openai.call("gpt-4o", response_model=Eval),
    anthropic.call("claude-3-5-sonnet-20240620", response_model=Eval),
]

evaluations: list[Eval] = [prompt.run(judge) for judge in judges]

for evaluation in evaluations:
    print(evaluation)
# Output:
# score=3.0 reasoning='The text is explicitly demeaning and discourages effort, which is harmful.'
# score=2.5 reasoning='Discouraging, insulting laziness, and implying inability. Promotes negativity and is demeaning.'
