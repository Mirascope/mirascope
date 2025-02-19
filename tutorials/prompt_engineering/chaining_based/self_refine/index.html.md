# Self-Refine: Enhancing LLM Outputs Through Iterative Self-Improvement

This recipe demonstrates how to implement the Self-Refine technique using Large Language Models (LLMs) with Mirascope. Self-Refine is a prompt engineering method that enhances an LLM's output by iteratively generating feedback and improving its responses.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
<a href="https://arxiv.org/pdf/2303.17651">Self-refine</a> is a prompt engineering technique where a model gives feedback about its answer and uses the feedback to generate a new answer. This self refinement can take place multiple times to generate the final answer. Self-refine is helpful for reasoning, coding, and generation tasks.
</p>
</div>

## Basic Self-Refine Implementation

Let's start with a basic implementation of Self-Refine using Mirascope:




```python
from mirascope.core import openai, prompt_template
from mirascope.core.openai import OpenAICallResponse


@openai.call(model="gpt-4o-mini")
def call(query: str) -> str:
    return query


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Here is a query and a response to the query. Give feedback about the answer,
    noting what was correct and incorrect.
    Query:
    {query}
    Response:
    {response}
    """
)
def evaluate_response(query: str, response: OpenAICallResponse): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    For this query:
    {query}
    The following response was given:
    {response}
    Here is some feedback about the response:
    {feedback}

    Consider the feedback to generate a new response to the query.
    """
)
def generate_new_response(
    query: str, response: OpenAICallResponse
) -> openai.OpenAIDynamicConfig:
    feedback = evaluate_response(query, response)
    return {"computed_fields": {"feedback": feedback}}


def self_refine(query: str, depth: int) -> str:
    response = call(query)
    for _ in range(depth):
        response = generate_new_response(query, response)
    return response.content


query = """Olivia has $23. She bought five bagels for $3 each.
How much money does she have left?"""
print(self_refine(query, 1))
```

    To determine how much money Olivia has left after her purchase, let's break it down step by step:
    
    1. **Starting Amount**: Olivia has $23 initially.
    2. **Cost of Bagels**: She bought 5 bagels at $3 each. The total spent on bagels is calculated as:
       \[
       5 \times 3 = 15 \text{ dollars}
       \]
    3. **Amount Left**: Now, we subtract the total amount spent on the bagels from Olivia's starting amount:
       \[
       23 - 15 = 8 \text{ dollars}
       \]
    
    Therefore, after buying the bagels, Olivia has **$8 remaining**.


## Enhanced Self-Refine with Response Model

Now, let's improve our implementation by adding a response model to structure the output:



```python
from pydantic import BaseModel, Field


class MathSolution(BaseModel):
    steps: list[str] = Field(..., description="The steps taken to solve the problem")
    final_answer: float = Field(..., description="The final numerical answer")


@openai.call(model="gpt-4o-mini", response_model=MathSolution)
@prompt_template(
    """
    For this query:
    {query}
    The following response was given:
    {response}
    Here is some feedback about the response:
    {feedback}

    Consider the feedback to generate a new response to the query.
    Provide the solution steps and the final numerical answer.
    """
)
def enhanced_generate_new_response(
    query: str, response: OpenAICallResponse
) -> openai.OpenAIDynamicConfig:
    feedback = evaluate_response(query, response)
    return {"computed_fields": {"feedback": feedback}}


def enhanced_self_refine(query: str, depth: int) -> MathSolution:
    response = call(query)
    for _ in range(depth):
        solution = enhanced_generate_new_response(query, response)
        response = f"Steps: {solution.steps}\nFinal Answer: {solution.final_answer}"
    return solution


# Example usage
result = enhanced_self_refine(query, 1)
print(result)
```

    steps=['Olivia has $23.', 'She bought five bagels for $3 each.', 'Calculate the total cost for the bagels: 5 bagels * $3/bagel = $15.', 'Subtract the total cost of the bagels from the amount of money she had: $23 - $15 = $8.'] final_answer=8.0


This enhanced version introduces a MathSolution response model to structure the output, providing a clearer separation between solution steps and the final answer.

## Benefits and Considerations

The Self-Refine implementation offers several advantages:

1. Improved accuracy through iterative refinement of responses.
2. Enhanced reasoning capabilities, especially for complex problems.
3. Potential for generating more detailed and step-by-step solutions.

When implementing this technique, consider:

- Balancing the number of refinement iterations with computational cost and time constraints.
- Tailoring the feedback prompts to focus on specific aspects of improvement relevant to your use case.
- Experimenting with different model parameters (e.g., temperature) for initial responses vs. refinement steps.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Essay Writing</b>: Use Self-Refine to iteratively improve essay drafts, focusing on structure, argument coherence, and style.</li>
<li><b>Code Generation</b>: Apply the technique to generate, evaluate, and refine code snippets or entire functions.</li>
<li><b>Data Analysis Reports</b>: Enhance the quality and depth of data analysis reports through iterative self-improvement.</li>
<li><b>Product Descriptions</b>: Refine product descriptions to be more engaging, accurate, and tailored to target audiences.</li>
<li><b>Legal Document Drafting</b>: Improve the precision and comprehensiveness of legal documents through self-refinement.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Customizing the feedback prompts to focus on domain-specific criteria.
- Implementing different types of response models for various tasks (e.g., text generation, problem-solving).
- Combining Self-Refine with other techniques like Chain of Thought for more complex reasoning tasks.
- Developing a mechanism to halt refinement when improvements become marginal.

By leveraging Mirascope's call decorator, response models, and dynamic configuration, you can easily implement and customize the Self-Refine technique to enhance your LLM's output quality across a wide range of applications.
