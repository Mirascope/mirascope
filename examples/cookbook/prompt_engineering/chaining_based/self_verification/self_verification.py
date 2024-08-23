import asyncio
import random

from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", call_params={"temperature": random.uniform(0, 2)})
@prompt_template(
    "Answer the following question, going through it step by step: {query}"
)
async def zero_shot_cot(query: str): ...


class ProblemInfo(BaseModel):
    key_info: list[str] = Field(
        ...,
        description="""Key pieces of information needed to solve the problem.
        Each key info is written as a short phrase.""",
    )


@openai.call(model="gpt-4o-mini", response_model=ProblemInfo)
@prompt_template(
    """
    For the following question, identify the key pieces of information
    needed to answer the question.
    Question: {query}
    """
)
def identify_key_info(query: str): ...


class MaskedPrompts(BaseModel):
    masked_prompts: list[str] = Field(
        ...,
        description="""The original prompt with the specified key info replaced with X.
        Example:
        Prompt: Jane walked 6 miles today. It was a sunny day.
        Key info: How many miles Jane walked
        Masked Prompt: Jane walked X miles today. It was a sunny day.""",
    )


@openai.call(model="gpt-4o-mini", response_model=MaskedPrompts)
@prompt_template(
    """
    Generate one masked copy of the prompt for each piece of key info.
    The number of masked prompts you generate should be equal to the number of pieces
    of key info, and each masked prompt should mask one key piece of information.
    Prompt: {query}
    Key Info: {key_info}
    """
)
async def mask_prompt(query: str) -> openai.OpenAIDynamicConfig:
    key_info = identify_key_info(query).key_info
    return {"computed_fields": {"key_info": key_info}}


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    You will be given a masked prompt with some value Xd out, and the solution to
    the original problem. Return the prompt verbatim, but fill in the value for X
    according to what you see in the solution.
    USER:
    solution: {solution}
    masked prompt: {masked_prompt}
    """
)
async def fill_in_value(solution: str, masked_prompt: str): ...


class PromptComparison(BaseModel):
    score: int = Field(
        ...,
        description="""The number of variation prompts which are
                    semantically equivalent to the original prompt.
                    For numbers in the prompts, expect the same values, and for
                    quantitative words, only count semantically identical terms, such
                    as two times = double.""",
    )


@openai.call(model="gpt-4o-mini", response_model=PromptComparison)
@prompt_template(
    """
    SYSTEM:
    You will be given an original prompt and some variations of it. Return the
    number of variations which are semantically identical.
    USER:
    Original Prompt:
    {query}
    Variations:
    {numbered_variations}
    """
)
def score_variations(
    query: str, filled_in_prompts: list[str]
) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "numbered_variations": [
                f"{i+1}. {_}" for i, _ in enumerate(filled_in_prompts)
            ]
        }
    }


async def evaluate_solution(query: str, solution: str, masked_prompts: list[str]):
    tasks = [fill_in_value(solution, masked_prompt) for masked_prompt in masked_prompts]
    responses = await asyncio.gather(*tasks)
    filled_in_prompts = [response.content for response in responses]
    score = score_variations(query, filled_in_prompts).score
    return score


query = """Tim wanted to make lemonade for a pool party. For a gallon of lemonade,
his recipe called for 1 cup of fresh lemon juice. He found that 6 lemons would yield
1 cup of juice. He figured he would need to make 4 gallons of lemonade for the
party. His best friend Allen asked if Tim could make an extra gallon for him that
was twice as tart as the other gallons. How many lemons will Tim need?"""


async def self_verify(query: str, num_solutions: int):
    tasks = [mask_prompt(query)]
    tasks += [zero_shot_cot(query) for _ in range(num_solutions)]
    responses = await asyncio.gather(*tasks)
    masked_prompts = responses[0].masked_prompts  # type: ignore
    # Uncomment to see intermediate responses
    print(masked_prompts)
    cot_responses = [response.content for response in responses[1:]]  # type: ignore
    print(cot_responses)
    tasks = [
        evaluate_solution(query, solution, masked_prompts) for solution in cot_responses
    ]
    scores = await asyncio.gather(*tasks)
    print(scores)
    print(f"MAX SCORE:{len(masked_prompts)}")
    for cot_solution, score in zip(cot_responses, scores, strict=False):
        print(f"Solution:\n{cot_solution}\nScore:\n{score}\n")


asyncio.run(self_verify(query, 3))
# MAX SCORE:4
# Solution:
# Let's break down the problem step by step.

# 1. **Determine the total amount of lemonade needed:**
#    - Tim originally planned to make 4 gallons of lemonade.
#    - Allen asked for an extra gallon, making the total amount of lemonade:
#      \[
#      4 \text{ gallons} + 1 \text{ gallon} = 5 \text{ gallons}
#      \]

# 2. **Calculate the amount of lemon juice needed for 5 gallons:**
#    - Each gallon requires 1 cup of lemon juice.
#    - Therefore, for 5 gallons, the total amount of lemon juice needed is:
#      \[
#      5 \text{ gallons} \times 1 \text{ cup/gallon} = 5 \text{ cups of lemon juice}
#      \]

# 3. **Determine the amount of lemon juice needed for the extra tart gallon:**
#    - Allen's gallon is twice as tart as the others. This means it will require double the amount of lemon juice.
#    - Therefore, for the extra gallon, the amount of lemon juice needed is:
#      \[
#      1 \text{ cup} \times 2 = 2 \text{ cups of lemon juice}
#      \]

# 4. **Calculate the total amount of lemon juice needed:**
#    - For the 4 gallons, Tim needs 4 cups of lemon juice (1 cup each).
#    - For the extra tart gallon, he needs 2 cups of lemon juice.
#    - Thus, the total amount of lemon juice needed is:
#      \[
#      4 \text{ cups} + 2 \text{ cups} = 6 \text{ cups of lemon juice}
#      \]

# 5. **Determine how many lemons are needed to make 6 cups of lemon juice:**
#    - From the information given, 6 lemons yield 1 cup of lemon juice.
#    - To find out how many lemons are needed for 6 cups, we calculate:
#      \[
#      6 \text{ lemons/cup} \times 6 \text{ cups} = 36 \text{ lemons}
#      \]

# So, Tim will need a total of **36 lemons** to make the lemonade for the pool party, including the extra tart gallon for Allen.
# Score:
# 0

# Solution:
# Let's go through the problem step by step.

# 1. **Determine the amount of lemon juice needed for 4 gallons of lemonade.**
#    - According to Tim's recipe, 1 gallon of lemonade requires 1 cup of lemon juice.
#    - For 4 gallons, the total amount of lemon juice needed is:
#      \[
#      4 \text{ gallons} \times 1 \text{ cup/gallon} = 4 \text{ cups of lemon juice}
#      \]

# 2. **Calculate the number of lemons needed for 4 gallons of lemonade.**
#    - Tim found that 6 lemons yield 1 cup of juice.
#    - To find out how many lemons are needed for 4 cups of juice, we first determine how many cups of juice can be obtained from 6 lemons:
#      \[
#      6 \text{ lemons} \rightarrow 1 \text{ cup}
#      \]
#    - Therefore, for 4 cups of juice, the number of lemons required is:
#      \[
#      4 \text{ cups} \times 6 \text{ lemons/cup} = 24 \text{ lemons}
#      \]

# 3. **Determine the amount of lemon juice needed for the extra gallon that is twice as tart.**
#    - Since the extra gallon is supposed to be twice as tart, it will require twice the amount of lemon juice as a regular gallon.
#    - Therefore, for the extra gallon:
#      \[
#      1 \text{ gallon} \times 2 \text{ cups/gallon} = 2 \text{ cups of lemon juice}
#      \]

# 4. **Calculate the number of lemons needed for the extra gallon.**
#    - Using the same conversion as before (6 lemons yield 1 cup of juice), we find out how many lemons are needed for 2 cups of juice:
#      \[
#      2 \text{ cups} \times 6 \text{ lemons/cup} = 12 \text{ lemons}
#      \]

# 5. **Calculate the total number of lemons needed.**
#    - Now, we can find the total number of lemons needed for both the 4 gallons of lemonade and the extra gallon:
#      \[
#      24 \text{ lemons (for 4 gallons)} + 12 \text{ lemons (for extra gallon)} = 36 \text{ lemons}
#      \]

# Thus, Tim will need a total of **36 lemons** to make the lemonade for the pool party and the extra tart gallon for Allen.
# Score:
# 4

# Solution:
# Let's break this down step by step to determine how many lemons Tim will need.

# ### Step 1: Determine the amount of lemon juice needed for 4 gallons of lemonade.

# The recipe calls for **1 cup of fresh lemon juice** for **1 gallon of lemonade**. Therefore, for **4 gallons**, Tim will need:

# \[
# 4 \text{ gallons} \times 1 \text{ cup/gallon} = 4 \text{ cups of lemon juice}
# \]

# ### Step 2: Calculate the lemon juice needed for Allen's extra gallon.

# Allen wants an extra gallon that is **twice as tart**. To make it twice as tart, Tim will need **2 cups of lemon juice** for that gallon (since the standard recipe uses 1 cup for 1 gallon).

# ### Step 3: Find the total amount of lemon juice needed.

# Now, we add the lemon juice needed for both Tim's and Allen's lemonade:

# \[
# 4 \text{ cups (for 4 gallons)} + 2 \text{ cups (for Allen's extra gallon)} = 6 \text{ cups of lemon juice}
# \]

# ### Step 4: Determine how many lemons are needed to yield 6 cups of juice.

# We know that **6 lemons yield 1 cup of juice**. To find out how many lemons are needed for **6 cups of juice**, we can set up the following calculation:

# \[
# \text{Number of lemons} = 6 \text{ lemons/cup} \times 6 \text{ cups} = 36 \text{ lemons}
# \]

# ### Conclusion

# Tim will need **36 lemons** to make 4 gallons of regular lemonade and 1 extra gallon that is twice as tart.
# Score:
# 0


# Intermediate responses

# masked_prompts = responses[0].masked_prompts
# > ['Tim wanted to make lemonade for a pool party. For X gallon of lemonade, his recipe called for 1 cup of fresh lemon juice. He found that 6 lemons would yield 1 cup of juice. He figured he would need to make 4 gallons of lemonade for the party. His best friend Allen asked if Tim could make an extra gallon for him that was twice as tart as the other gallons. How many lemons will Tim need?', 'Tim wanted to make lemonade for a pool party. For a gallon of lemonade, his recipe called for X cup of fresh lemon juice. He found that 6 lemons would yield 1 cup of juice. He figured he would need to make 4 gallons of lemonade for the party. His best friend Allen asked if Tim could make an extra gallon for him that was twice as tart as the other gallons. How many lemons will Tim need?', 'Tim wanted to make lemonade for a pool party. For a gallon of lemonade, his recipe called for 1 cup of fresh lemon juice. He found that X lemons would yield 1 cup of juice. He figured he would need to make 4 gallons of lemonade for the party. His best friend Allen asked if Tim could make an extra gallon for him that was twice as tart as the other gallons. How many lemons will Tim need?', 'Tim wanted to make lemonade for a pool party. For a gallon of lemonade, his recipe called for 1 cup of fresh lemon juice. He found that 6 lemons would yield 1 cup of juice. He figured he would need to make 4 gallons of lemonade for the party. His best friend Allen asked if Tim could make an extra X gallon for him that was twice as tart as the other gallons. How many lemons will Tim need?']

# print(cot_responses)
# > ["Let's break down the problem step by step.\n\n1. **Determine the total amount of lemonade needed:**\n   - Tim originally planned to make 4 gallons of lemonade.\n   - Allen asked for an extra gallon, making the total amount of lemonade:\n     \\[\n     4 \\text{ gallons} + 1 \\text{ gallon} = 5 \\text{ gallons}\n     \\]\n\n2. **Calculate the amount of lemon juice needed for 5 gallons:**\n   - Each gallon requires 1 cup of lemon juice.\n   - Therefore, for 5 gallons, the total amount of lemon juice needed is:\n     \\[\n     5 \\text{ gallons} \\times 1 \\text{ cup/gallon} = 5 \\text{ cups of lemon juice}\n     \\]\n\n3. **Determine the amount of lemon juice needed for the extra tart gallon:**\n   - Allen's gallon is twice as tart as the others. This means it will require double the amount of lemon juice.\n   - Therefore, for the extra gallon, the amount of lemon juice needed is:\n     \\[\n     1 \\text{ cup} \\times 2 = 2 \\text{ cups of lemon juice}\n     \\]\n\n4. **Calculate the total amount of lemon juice needed:**\n   - For the 4 gallons, Tim needs 4 cups of lemon juice (1 cup each).\n   - For the extra tart gallon, he needs 2 cups of lemon juice.\n   - Thus, the total amount of lemon juice needed is:\n     \\[\n     4 \\text{ cups} + 2 \\text{ cups} = 6 \\text{ cups of lemon juice}\n     \\]\n\n5. **Determine how many lemons are needed to make 6 cups of lemon juice:**\n   - From the information given, 6 lemons yield 1 cup of lemon juice.\n   - To find out how many lemons are needed for 6 cups, we calculate:\n     \\[\n     6 \\text{ lemons/cup} \\times 6 \\text{ cups} = 36 \\text{ lemons}\n     \\]\n\nSo, Tim will need a total of **36 lemons** to make the lemonade for the pool party, including the extra tart gallon for Allen.", "Let's go through the problem step by step.\n\n1. **Determine the amount of lemon juice needed for 4 gallons of lemonade.**\n   - According to Tim's recipe, 1 gallon of lemonade requires 1 cup of lemon juice.\n   - For 4 gallons, the total amount of lemon juice needed is:\n     \\[\n     4 \\text{ gallons} \\times 1 \\text{ cup/gallon} = 4 \\text{ cups of lemon juice}\n     \\]\n\n2. **Calculate the number of lemons needed for 4 gallons of lemonade.**\n   - Tim found that 6 lemons yield 1 cup of juice.\n   - To find out how many lemons are needed for 4 cups of juice, we first determine how many cups of juice can be obtained from 6 lemons:\n     \\[\n     6 \\text{ lemons} \\rightarrow 1 \\text{ cup}\n     \\]\n   - Therefore, for 4 cups of juice, the number of lemons required is:\n     \\[\n     4 \\text{ cups} \\times 6 \\text{ lemons/cup} = 24 \\text{ lemons}\n     \\]\n\n3. **Determine the amount of lemon juice needed for the extra gallon that is twice as tart.**\n   - Since the extra gallon is supposed to be twice as tart, it will require twice the amount of lemon juice as a regular gallon.\n   - Therefore, for the extra gallon:\n     \\[\n     1 \\text{ gallon} \\times 2 \\text{ cups/gallon} = 2 \\text{ cups of lemon juice}\n     \\]\n\n4. **Calculate the number of lemons needed for the extra gallon.**\n   - Using the same conversion as before (6 lemons yield 1 cup of juice), we find out how many lemons are needed for 2 cups of juice:\n     \\[\n     2 \\text{ cups} \\times 6 \\text{ lemons/cup} = 12 \\text{ lemons}\n     \\]\n\n5. **Calculate the total number of lemons needed.**\n   - Now, we can find the total number of lemons needed for both the 4 gallons of lemonade and the extra gallon:\n     \\[\n     24 \\text{ lemons (for 4 gallons)} + 12 \\text{ lemons (for extra gallon)} = 36 \\text{ lemons}\n     \\]\n\nThus, Tim will need a total of **36 lemons** to make the lemonade for the pool party and the extra tart gallon for Allen.", "Let's break this down step by step to determine how many lemons Tim will need.\n\n### Step 1: Determine the amount of lemon juice needed for 4 gallons of lemonade.\n\nThe recipe calls for **1 cup of fresh lemon juice** for **1 gallon of lemonade**. Therefore, for **4 gallons**, Tim will need:\n\n\\[\n4 \\text{ gallons} \\times 1 \\text{ cup/gallon} = 4 \\text{ cups of lemon juice}\n\\]\n\n### Step 2: Calculate the lemon juice needed for Allen's extra gallon.\n\nAllen wants an extra gallon that is **twice as tart**. To make it twice as tart, Tim will need **2 cups of lemon juice** for that gallon (since the standard recipe uses 1 cup for 1 gallon).\n\n### Step 3: Find the total amount of lemon juice needed.\n\nNow, we add the lemon juice needed for both Tim's and Allen's lemonade:\n\n\\[\n4 \\text{ cups (for 4 gallons)} + 2 \\text{ cups (for Allen's extra gallon)} = 6 \\text{ cups of lemon juice}\n\\]\n\n### Step 4: Determine how many lemons are needed to yield 6 cups of juice.\n\nWe know that **6 lemons yield 1 cup of juice**. To find out how many lemons are needed for **6 cups of juice**, we can set up the following calculation:\n\n\\[\n\\text{Number of lemons} = 6 \\text{ lemons/cup} \\times 6 \\text{ cups} = 36 \\text{ lemons}\n\\]\n\n### Conclusion\n\nTim will need **36 lemons** to make 4 gallons of regular lemonade and 1 extra gallon that is twice as tart."]

# scores
# > [0, 4, 0]
