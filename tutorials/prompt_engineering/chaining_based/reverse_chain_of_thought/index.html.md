# Reverse Chain of Thought: Enhancing LLM Reasoning with Self-Reflection

This recipe demonstrates how to implement the Reverse Chain of Thought technique using Large Language Models (LLMs) with Mirascope. Reverse Chain of Thought is a prompt engineering method that enhances an LLM's reasoning capabilities by encouraging it to reflect on and correct its own thought process.

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
Reverse chain of thought is a prompt engineering technique where a <a href="https://arxiv.org/abs/2201.11903">chain of thought</a> call is made for a query, then we attempt to reconstruct the query from the attempted solution. Both the original and reconstructed query are broken down into their individual conditions, and each condition is cross-referenced with the totality of conditions for the other query to determine the existence of overlooked facts or hallucinations. The questions themselves are also compared to ensure that the two queries not only share the context but also ask the same question. This fine-grained comparison is used in a final prompt.
</p>
<p>
In the <a href="https://arxiv.org/pdf/2305.11499">original paper</a>, no prompt was given for the case when mistakes do not exist, so we took the liberty of asking the model to repeat a solution without mistakes. 
</p>
<p>
Reverse chain of thought is a technique that works for any prompt which has shown signs of susceptibility to hallucinations or misinterpretations in its initial attempts to answer the question.
</p>
</div>

## Implementation

Let's implement the Reverse Chain of Thought technique using Mirascope:





```python
import asyncio

from mirascope.core import openai, prompt_template
from mirascope.core.openai import OpenAICallResponse
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field


@openai.call(model="gpt-4o-mini")
def zero_shot_cot(query: str) -> str:
    return f"{query} Let's think step by step."


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    USER:
    Give the concrete prompt (problem) that can generate this answer.
    The problem should contain all basic and necessary information and correspond to the answer.
    The problem can only ask for one result.

    {response}
    """
)
def reconstruct_query(response: str): ...


class Decomposition(BaseModel):
    conditions: list[str] = Field(
        ..., description="A list of conditions of the problem."
    )


@openai.call(
    model="gpt-4o-mini",
    response_model=Decomposition,
    call_params={"tool_choice": "required"},
)
@prompt_template(
    """
    Please list the conditions of the problem. There may be multiple conditions.
    Do not list conditions not related to calculations, but list all necessary conditions.
    The format should be a list of conditions with one condition per item.

    {query}
    """
)
async def decompose_query(query: str): ...


class Comparison(BaseModel):
    condition: str = Field(
        ..., description="The original condition the comparison was made with, verbatim"
    )
    deducible: bool = Field(
        ...,
        description="Whether the condition is deducible from the list of other conditions.",
    )
    illustration: str = Field(
        ...,
        description="A quick illustration of the reason the condition is/isn't deducible from the list of other conditions.",
    )


@openai.call(
    model="gpt-4o-mini",
    response_model=Comparison,
    call_params={"tool_choice": "required"},
)
@prompt_template(
    """
    Given a candidate condition: '{condition}'

    Here is a condition list: '{condition_list}'

    From a mathematical point of view, can this candidate condition be deduced from the condition list?
    Please illustrate your reason and answer True or False.
    """
)
async def compare_conditions(condition: str, condition_list: list[str]): ...


@openai.call(
    model="gpt-4o-mini", response_model=bool, call_params={"tool_choice": "required"}
)
@prompt_template(
    """
    Q1: {original_problem}
    Q2: {reconstructed_problem}
    
    From a mathematical point of view, are these two problems asking the same thing at the end?
    """
)
def compare_questions(original_problem: str, reconstructed_problem: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    MESSAGES: {history}
    USER:
    {mistakes_prompt}
    {overlooked_prompt}
    {hallucination_prompt}
    {misinterpretation_prompt}
    """
)
async def fine_grained_comparison(
    history: list[ChatCompletionMessageParam], query: str, reconstructed_query: str
) -> openai.OpenAIDynamicConfig:
    # Decompose both queries into conditions
    original_conditions, reconstructed_conditions = [
        response.conditions
        for response in await asyncio.gather(
            decompose_query(query), decompose_query(reconstructed_query)
        )
    ]

    # Identify overlooked/hallucinated conditions and misinterpretation of question
    overlooking_tasks = [
        compare_conditions(original_condition, reconstructed_conditions)
        for original_condition in original_conditions
    ]
    hallucination_tasks = [
        compare_conditions(reconstructed_condition, original_conditions)
        for reconstructed_condition in reconstructed_conditions
    ]
    full_comparison = await asyncio.gather(*(overlooking_tasks + hallucination_tasks))

    question_misinterpretation = compare_questions(query, reconstructed_query)

    overlooked_comparisons = [
        comparison
        for comparison in full_comparison[: len(original_conditions)]
        if not comparison.deducible
    ]
    hallucination_comparisons = [
        comparison
        for comparison in full_comparison[len(original_conditions) :]
        if not comparison.deducible
    ]

    # Fill out prompt depending on the comparisons
    if (
        not question_misinterpretation
        and not overlooked_comparisons
        and not hallucination_comparisons
    ):
        mistakes_prompt = """There are no mistakes in your interpretation of the prompt.
        Repeat your original solution verbatim."""
        overlooked_prompt = ""
        hallucination_prompt = ""
        misinterpretation_prompt = ""
    else:
        mistakes_prompt = (
            "Here are the mistakes and reasons in your answer to the problem.\n"
        )

        if overlooked_comparisons:
            conditions = [comparison.condition for comparison in overlooked_comparisons]
            illustrations = [
                comparison.illustration for comparison in overlooked_comparisons
            ]
            overlooked_prompt = f"""
            Overlooked Conditions:
            You have ignored some real conditions:
            {conditions}
            The real problem has the conditions:
            {original_conditions}
            You should consider all real conditions in the problem.
            Here are the detailed reasons:
            {illustrations}"""
        else:
            overlooked_prompt = ""

        if hallucination_comparisons:
            conditions = [
                comparison.condition for comparison in hallucination_comparisons
            ]
            illustrations = [
                comparison.illustration for comparison in overlooked_comparisons
            ]
            hallucination_prompt = f"""
            Hallucinated Conditions
            You use some wrong candidate conditions:
            {conditions}
            They all can not be deduced from the true condition list.
            The real problem has the conditions:
            {original_conditions}
            You should consider all real conditions in the problem.
            Here are the detailed reasons:
            {illustrations}"""
        else:
            hallucination_prompt = ""

        if question_misinterpretation:
            misinterpretation_prompt = f"""
            You misunderstood the question.
            You think the question is: {reconstructed_query}.
            But the real question is: {query}
            They are different. You should consider the original question."""
        else:
            misinterpretation_prompt = ""
    return {
        "computed_fields": {
            "mistakes_prompt": mistakes_prompt,
            "overlooked_prompt": overlooked_prompt,
            "hallucination_prompt": hallucination_prompt,
            "misinterpretation_prompt": misinterpretation_prompt,
        }
    }


async def reverse_cot(query: str) -> OpenAICallResponse:
    cot_response = zero_shot_cot(query=query)
    reconstructed_query_response = reconstruct_query(cot_response.content)
    history = cot_response.messages + reconstructed_query_response.messages
    response = await fine_grained_comparison(
        history=history,
        query=query,
        reconstructed_query=reconstructed_query_response.content,
    )
    return response


query = """At the trip to the county level scavenger hunt competition 90 people \
were required to split into groups for the competition to begin. To break \
people up into smaller groups with different leaders 9-person groups were \
formed. If 3/5 of the number of groups each had members bring back 2 seashells each \
how many seashells did they bring?"""

print(await reverse_cot(query=query))
```

    Thank you for your feedback! Based on your clarifications, here’s a revised problem prompt that corresponds to your original question while considering all the necessary conditions:
    
    ---
    
    **Problem Prompt:**
    
    At the trip to the county-level scavenger hunt competition, there are 90 participants who need to be divided into groups for the event to start. Each group consists of 9 people. If \( \frac{3}{5} \) of the total number of groups formed contributed by bringing back seashells, and each member of those groups brought back 2 seashells each, how many seashells were brought back in total?
    
    ---
    
    This prompt encapsulates all essential components of the problem. It clarifies the number of participants, how they are grouped, the fraction of groups contributing, and the number of seashells collected by each member, leading to the final calculation. Let's go through the reasoning for clarity:
    
    1. **Total Participants**: 90 people.
    2. **Groups Formed**: Each group has 9 members, so:
       \[
       \text{Number of groups} = \frac{90}{9} = 10
       \]
    3. **Groups Contributing Shells**: \( \frac{3}{5} \) of the total groups contributed:
       \[
       \text{Groups contributing} = 10 \times \frac{3}{5} = 6
       \]
    4. **Total Members in Contributing Groups**: Each contributing group has 9 members:
       \[
       \text{Total members contributing} = 6 \times 9 = 54
       \]
    5. **Total Seashells Collected**: Each member brought back 2 seashells:
       \[
       \text{Total seashells} = 54 \times 2 = 108
       \]
    
    Thus, the total number of seashells brought back is:
    
    \[
    \boxed{108}
    \] 
    
    This approach correctly follows the sequence of logical deductions based on the problem's premise. Thank you for your guidance!


This implementation consists of several key functions:

1. `zero_shot_cot`: Generates an initial chain of thought response.
2. `reconstruct_query`: Attempts to reconstruct the original query from the chain of thought response.
3. `decompose_query`: Breaks down a query into its individual conditions.
4. `compare_conditions`: Compares individual conditions to determine if they are deducible from a list of other conditions.
5. `compare_questions`: Checks if two questions are asking the same thing.
6. `fine_grained_comparison`: Performs a detailed comparison between the original and reconstructed queries, identifying overlooked conditions, hallucinations, and misinterpretations.
7. `reverse_cot`: Orchestrates the entire Reverse Chain of Thought process.

## Benefits and Considerations

The Reverse Chain of Thought implementation offers several advantages:

1. Improved accuracy by identifying and correcting overlooked conditions, hallucinations, and misinterpretations.
2. Enhanced reasoning capabilities through self-reflection and error correction.
3. More robust problem-solving, especially for complex or ambiguous queries.

When implementing this technique, consider:

- Balancing the computational cost of multiple LLM calls with the improved accuracy.
- Fine-tuning the prompts for each step to optimize the reflection and correction process.
- Adapting the technique for different types of problems or domains.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Complex Problem Solving</b>: Use Reverse Chain of Thought for multi-step problems in fields like physics or engineering.</li>
<li><b>Legal Analysis</b>: Apply the technique to enhance the accuracy of legal interpretations and argumentation.</li>
<li><b>Medical Diagnosis</b>: Implement Reverse Chain of Thought to improve the reliability of symptom analysis and potential diagnoses.</li>
<li><b>Financial Modeling</b>: Enhance the accuracy of financial predictions and risk assessments by identifying overlooked factors.</li>
<li><b>Educational Assessment</b>: Use the technique to generate and validate complex exam questions and their solutions.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Tailoring the decomposition and comparison steps to your domain for better performance.
- Implementing a feedback loop to continuously improve the quality of the Reverse Chain of Thought responses.
- Combining Reverse Chain of Thought with other techniques like Self-Ask or Self-Consistency for even more powerful reasoning capabilities.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the Reverse Chain of Thought technique to enhance your LLM's reasoning capabilities across a wide range of applications.

