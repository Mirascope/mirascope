# DiVeRSe: Enhancing LLM Reasoning with Prompt Variations

This recipe demonstrates how to implement the DiVeRSe (Diverse Verifier on Reasoning Steps) technique using Large Language Models (LLMs) with Mirascope. DiVeRSe is a prompt engineering method that enhances an LLM's reasoning capabilities by generating multiple reasoning chains from variations of the original prompt.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
<li><a href="../../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
<a href="https://arxiv.org/abs/2305.11862">DiVeRSe</a> is a variant of the self-consistency prompt engineering technique. Instead of generating multiple chains from the same prompt, DiVeRSe creates variations of the original prompt to generate different reasoning chains. This approach can significantly improve the LLM's ability to reason about complex problems by considering multiple perspectives and phrasings of the same question.
</p>
</div>

## Implementation

Let's implement the DiVeRSe technique using Mirascope:




```python
import asyncio

from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field


class PromptVariations(BaseModel):
    variations: list[str] = Field(..., description="Variations of the original prompt")


@openai.call(model="gpt-4o-mini", response_model=PromptVariations)
@prompt_template(
    """
    Return the {num_prompts} alternate variations of the prompt which retain the
    full meaning but uses different phrasing.
    Prompt: {prompt}
    """
)
def get_prompt_variations(prompt: str, num_prompts: int): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Answer the following question going step by step:
    {query}
    """
)
async def zero_shot_cot(query: str): ...


class ResponseDetails(BaseModel):
    solution_number: int = Field(
        ..., description="The actual number given as the answer in a solution."
    )
    correctness_probability: float = Field(
        ...,
        ge=0,
        le=1,
        description="An estimated probability that the given solution is correct from 0.0 to 1.0",
    )


@openai.call(model="gpt-4o-mini", response_model=ResponseDetails)
@prompt_template(
    """
    Here is a query and a response which attempts to answer the query.
    Prompt: {query}
    Response: {response}

    Extract the raw numerical value of the answer given by the response, and also
    give an estimate between 0.0 and 1.0 of the probability that this solution
    is correct.
    """
)
async def evaluate_response(query: str, response: str): ...


async def diverse(query: str, num_variations: int) -> str:
    # Gather the variations of the prompt
    alternate_variations = get_prompt_variations(query, num_variations - 1)
    all_variations = alternate_variations.variations + [query]

    # Generate a unique reasoning chain for each prompt variation with CoT
    cot_tasks = [zero_shot_cot(prompt) for prompt in all_variations]
    cot_responses = [response.content for response in await asyncio.gather(*cot_tasks)]

    # Evaluate each reasoning chain
    eval_tasks = [
        evaluate_response(query, cot_response) for cot_response in cot_responses
    ]
    eval_responses = await asyncio.gather(*eval_tasks)

    response_scores = {}
    for eval_response in eval_responses:
        if eval_response.solution_number not in response_scores:
            response_scores[eval_response.solution_number] = 0
        response_scores[eval_response.solution_number] += (
            eval_response.correctness_probability
        )
    best_response = max(response_scores.keys(), key=lambda k: response_scores[k])
    return best_response


async def run_diverse(prompt, num_variations=3) -> str:
    response = await diverse(prompt, num_variations)
    return response


query = """
A committee of 3 people must be formed from a pool of 6 people, but Amy and Bob do not
get along and should not be on the committee at the same time. How many viable
combinations are there?
"""

print(await run_diverse(query))
```

    16




This implementation consists of several key components:

1. `get_prompt_variations`: Generates variations of the original prompt.
2. `zero_shot_cot`: Implements zero-shot chain-of-thought reasoning for each prompt variation.
3. `evaluate_response`: Evaluates each reasoning chain and assigns a probability of correctness.
4. `diverse`: Orchestrates the DiVeRSe technique by generating prompt variations, creating reasoning chains, and selecting the best response.

## Benefits and Considerations

The DiVeRSe implementation offers several advantages:

1. Improved reasoning by considering multiple phrasings of the same problem.
2. Enhanced robustness against potential misinterpretations of the original prompt.
3. Potential for more accurate responses in complex reasoning tasks.

When implementing this technique, consider:

- Balancing the number of prompt variations with computational cost and time constraints.
- Adjusting the evaluation criteria for different types of problems (e.g., numerical vs. categorical answers).
- Fine-tuning the prompt variation generation to ensure meaningful diversity while maintaining the original question's intent.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Complex Problem Solving</b>: Use DiVeRSe for multi-step problems in fields like mathematics, physics, or engineering.</li>
<li><b>Legal Document Analysis</b>: Apply the technique to interpret complex legal scenarios from multiple perspectives.</li>
<li><b>Market Research</b>: Generate diverse interpretations of consumer feedback or survey responses.</li>
<li><b>Educational Assessment</b>: Create and evaluate multiple versions of exam questions to ensure fairness and comprehension.</li>
<li><b>Scientific Hypothesis Generation</b>: Use DiVeRSe to approach research questions from various angles, potentially uncovering novel insights.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Tailoring the prompt variation generation to your domain for better performance.
- Experimenting with different evaluation methods for the reasoning chains.
- Implementing a feedback loop to refine the prompt variation process based on the accuracy of final answers.
- Combining DiVeRSe with other techniques like Self-Ask or Sim to M for even more nuanced reasoning capabilities.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the DiVeRSe technique to enhance your LLM's ability to reason about complex problems across a wide range of applications.


