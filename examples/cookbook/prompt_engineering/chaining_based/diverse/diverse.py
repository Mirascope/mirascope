import asyncio

from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


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


async def diverse(query: str, num_variations: int):
    # Gather the variations of the prompt
    alternate_variations = get_prompt_variations(query, num_variations - 1)
    # Uncomment to see intermediate steps
    # print(alternate_variations)
    all_variations = alternate_variations.variations + [query]

    # Generate a unique reasoning chain for each prompt variation with CoT
    cot_tasks = [zero_shot_cot(prompt) for prompt in all_variations]
    cot_responses = [response.content for response in await asyncio.gather(*cot_tasks)]
    # print(cot_responses)

    # Evaluate each reasoning chain
    eval_tasks = [
        evaluate_response(query, cot_response) for cot_response in cot_responses
    ]
    eval_responses = await asyncio.gather(*eval_tasks)
    # print(eval_responses)

    response_scores = {}
    for eval_response in eval_responses:
        if eval_response.solution_number not in response_scores:
            response_scores[eval_response.solution_number] = 0
        response_scores[eval_response.solution_number] += (
            eval_response.correctness_probability
        )
    # print(response_scores)
    best_response = max(response_scores, key=response_scores.get)  # type: ignore
    return best_response


async def run_self_consistency(prompt, num_variations=3):
    return await diverse(prompt, num_variations)


query = """
A committee of 3 people must be formed from a pool of 6 people, but Amy and Bob do not
get along and should not be on the committee at the same time. How many viable
combinations are there?
"""

print(asyncio.run(run_self_consistency(query)))
# > 16


# Intermediate Steps

# alternate_variations = get_prompt_variations(query, num_variations - 1)
# > variations=['A group of 3 individuals needs to be selected from a total of 6, but Amy and Bob cannot serve on the committee together due to their conflict. What are the possible combinations?', 'We need to establish a committee of 3 members from a selection of 6 individuals, with the stipulation that Amy and Bob must not both be included in the committee. How many suitable combinations can be created?']

# cot_responses = [response.content for response in await asyncio.gather(*cot_tasks)]
# > ["To find the number of possible combinations for selecting a committee of 3 individuals from 6, with the constraint that Amy (A) and Bob (B) cannot be selected together, we can break down the process step by step.\n\n### Step 1: Identify Total Individuals\nWe have the following individuals:\n- A (Amy)\n- B (Bob)\n- C\n- D\n- E\n- F\n\n### Step 2: Calculate Total Combinations Without Constraints\nFirst, we’ll calculate the total number of combinations of 3 individuals from 6 without any restrictions. This can be done using the combination formula \\( C(n, r) = \\frac{n!}{r!(n-r)!} \\), where \\( n \\) is the total number of individuals, and \\( r \\) is the number of individuals to choose.\n\nFor our scenario:\n\\[\nC(6, 3) = \\frac{6!}{3!(6-3)!} = \\frac{6 \\times 5 \\times 4}{3 \\times 2 \\times 1} = 20\n\\]\n\n### Step 3: Consider the Constraint\nNow we need to exclude the combinations where both Amy and Bob are included in the selection. To do this, we will calculate how many combinations include both A and B.\n\n### Step 4: Count Combinations Including Both A and B\nIf both A and B are selected, we need to choose 1 more individual from the remaining individuals {C, D, E, F} (4 individuals remaining).\n\nWe can compute the number of ways to choose 1 individual from 4:\n\\[\nC(4, 1) = 4\n\\]\nThe possible combinations that include both A and B are:\n1. A, B, C\n2. A, B, D\n3. A, B, E\n4. A, B, F\n\n### Step 5: Subtract Invalid Combinations from Total\nNow, we reduce the total combinations of 20 by the 4 combinations that include both A and B:\n\\[\n\\text{Valid combinations} = \\text{Total combinations} - \\text{Combinations including A and B}\n\\]\n\\[\n\\text{Valid combinations} = 20 - 4 = 16\n\\]\n\n### Final Step: List the Valid Combinations\nFor clarity, let's list the valid combinations that meet the criteria of not having both A and B together:\n\n1. A, C, D\n2. A, C, E\n3. A, C, F\n4. A, D, E\n5. A, D, F\n6. A, E, F\n7. B, C, D\n8. B, C, E\n9. B, C, F\n10. B, D, E\n11. B, D, F\n12. B, E, F\n13. C, D, E\n14. C, D, F\n15. C, E, F\n16. D, E, F\n\n### Conclusion\nThus, the total number of valid combinations, ensuring Amy and Bob are not serving together, is **16**.", 'To solve the problem of selecting a committee of 3 members from a group of 6 individuals, with the condition that Amy and Bob cannot both be included, we can break down the solution into steps.\n\n**Step 1: Count total combinations without restrictions.**\nWe first calculate the total number of ways to choose 3 members from the 6 individuals without any restrictions. We can use the binomial coefficient formula:\n\n\\[\n\\binom{n}{k} = \\frac{n!}{k!(n-k)!}\n\\]\n\nIn this case, \\( n = 6 \\) and \\( k = 3 \\):\n\n\\[\n\\binom{6}{3} = \\frac{6!}{3!(6-3)!} = \\frac{6 \\times 5 \\times 4}{3 \\times 2 \\times 1} = 20\n\\]\n\nSo, there are 20 ways to select any 3 individuals from 6.\n\n**Step 2: Count combinations including both Amy and Bob.**\nNext, we find the number of combinations where both Amy and Bob are included in the committee. If Amy and Bob are both included, we need to choose 1 more member from the remaining 4 individuals (since there are originally 6 individuals and 2 spots filled by Amy and Bob).\n\nThe number of ways to choose 1 member from the remaining 4 is:\n\n\\[\n\\binom{4}{1} = 4\n\\]\n\nThus, there are 4 combinations that include both Amy and Bob.\n\n**Step 3: Calculate valid combinations.**\nTo find the number of suitable combinations that meet the requirement of not having both Amy and Bob on the committee, we take the total combinations and subtract the combinations that include both Amy and Bob:\n\n\\[\n\\text{Valid combinations} = \\text{Total combinations} - \\text{Combinations with Amy and Bob}\n\\]\n\nSubstituting the values we found:\n\n\\[\n\\text{Valid combinations} = 20 - 4 = 16\n\\]\n\nTherefore, the number of suitable combinations of the committee that can be created under the given restrictions is:\n\n\\[\n\\boxed{16}\n\\]', "To solve the problem of forming a committee of 3 people from a pool of 6 people where Amy and Bob cannot be on the committee together, we can break down the solution into several steps:\n\n1. **Identify the members of the pool**:\n   - Let's label the 6 people as A (Amy), B (Bob), C, D, E, F (the others).\n\n2. **Calculate the total number of combinations without restrictions**:\n   - The total number of ways to choose 3 people from 6 is given by the combination formula:\n     \\[\n     \\binom{n}{r} = \\frac{n!}{r!(n-r)!}\n     \\]\n   - Here, \\( n = 6 \\) and \\( r = 3 \\):\n     \\[\n     \\binom{6}{3} = \\frac{6!}{3!3!} = \\frac{6 \\times 5 \\times 4}{3 \\times 2 \\times 1} = 20\n     \\]\n   - So, there are 20 ways to choose 3 people from 6 without any restrictions.\n\n3. **Account for the restriction (Amy and Bob can't be together)**:\n   - We need to calculate the number of combinations where both Amy and Bob are included, and then subtract this from the total.\n\n4. **Calculate the combinations where both Amy and Bob are on the committee**:\n   - If both Amy and Bob are on the committee, we only need to choose 1 more member from the remaining pool of 4 people (C, D, E, F).\n   - The number of ways to choose 1 additional member from 4 is:\n     \\[\n     \\binom{4}{1} = 4\n     \\]\n   - There are 4 ways to form a committee including both Amy and Bob.\n\n5. **Subtract the restricted combinations from the total**:\n   - The total valid combinations will therefore be:\n     \\[\n     \\text{Total combinations} - \\text{Combinations with Amy and Bob together} = 20 - 4 = 16\n     \\]\n\n6. **Final answer**:\n   - Thus, the number of viable combinations for the committee of 3 people, without both Amy and Bob being included together, is **16**.\n\nIn conclusion, the number of viable combinations is **16**."]

# eval_responses = await asyncio.gather(*eval_tasks)
# > [ResponseDetails(solution_number=16, correctness_probability=0.95), ResponseDetails(solution_number=16, correctness_probability=0.95), ResponseDetails(solution_number=16, correctness_probability=0.95)]

# response_scores
# {16: 2.8499999999999996}
