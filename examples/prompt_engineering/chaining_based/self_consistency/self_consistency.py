import asyncio
from collections import Counter

from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template

few_shot_examples = """
Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done,
there will be 21 trees. How many trees did the grove workers plant today?
A: We start with 15 trees. Later we have 21 trees. The difference must be the number of trees they planted.
So, they must have planted 21 - 15 = 6 trees. The answer is 6.
Q: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?
A: There are 3 cars in the parking lot already. 2 more arrive. Now there are 3 + 2 = 5 cars. The answer is 5.
Q: Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?
A: Leah had 32 chocolates and Leah’s sister had 42. That means there were originally 32 + 42 = 74
chocolates. 35 have been eaten. So in total they still have 74 - 35 = 39 chocolates. The answer is 39.
Q: Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops
did Jason give to Denny?
A: Jason had 20 lollipops. Since he only has 12 now, he must have given the rest to Denny. The number of
lollipops he has given to Denny must have been 20 - 12 = 8 lollipops. The answer is 8.
Q: Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does
he have now?
A: He has 5 toys. He got 2 from mom, so after that he has 5 + 2 = 7 toys. Then he got 2 more from dad, so
in total he has 7 + 2 = 9 toys. The answer is 9.
Q: There were nine computers in the server room. Five more computers were installed each day, from
monday to thursday. How many computers are now in the server room?
A: There are 4 days from monday to thursday. 5 computers were added each day. That means in total 4 * 5 =
20 computers were added. There were 9 computers in the beginning, so now there are 9 + 20 = 29 computers.
The answer is 29.
Q: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many
golf balls did he have at the end of wednesday?
A: Michael initially had 58 balls. He lost 23 on Tuesday, so after that he has 58 - 23 = 35 balls. On
Wednesday he lost 2 more so now he has 35 - 2 = 33 balls. The answer is 33.
"""


@openai.call(model="gpt-4o-mini", call_params={"temperature": 0.5})
@prompt_template(
    """
    Some examples on how to think step by step:
    {few_shot_examples}

    Answer the following question, thinking step by step:
    {query}
    """
)
async def chain_of_thought(query: str) -> openai.OpenAIDynamicConfig:
    return {"computed_fields": {"few_shot_examples": few_shot_examples}}


class Solution(BaseModel):
    solution_value: int = Field(
        ..., description="The actual number of a solution to a math problem."
    )


@openai.call(model="gpt-4o-mini", response_model=Solution)
@prompt_template(
    """
    Extract just the number of a solution to a math problem.
    For example, for the solution:
    Michael initially had 58 balls. He lost 23 on Tuesday, so after that he has
    58 - 23 = 35 balls. On Wednesday he lost 2 more so now he has 35 - 2 = 33 balls.
    The answer is 33.
    
    You would extract 33.

    Solution to extract from:
    {response}
    """
)
async def extract_number(response: str): ...


def most_frequent(lst):
    """Returns the most frequent element in a list."""
    counter = Counter(lst)
    most_common = counter.most_common(1)
    return most_common[0][0] if most_common else None


async def self_consistency(query: str, num_samples: int):
    cot_tasks = [chain_of_thought(query) for _ in range(num_samples)]
    cot_responses = [response.content for response in await asyncio.gather(*cot_tasks)]
    # Uncomment to see intermediate responses
    # for response in cot_responses:
    #     print(response)
    extract_number_tasks = [extract_number(response) for response in cot_responses]
    response_numbers = [
        response.solution_value
        for response in await asyncio.gather(*extract_number_tasks)
    ]
    return most_frequent(response_numbers)


query = """Olivia has $23. She bought five bagels for $3 each.
How much money does she have left?"""

print(asyncio.run(self_consistency(query=query, num_samples=5)))
# > 8


# Intermediate Responses

# cot_responses
# To find out how much money Olivia has left after buying the bagels, we can follow these steps:

# 1. **Determine the total cost of the bagels**: Olivia bought 5 bagels, and each bagel costs $3.
#    - Total cost = Number of bagels × Cost per bagel
#    - Total cost = 5 × 3 = $15

# 2. **Subtract the total cost from Olivia's initial amount**: Olivia started with $23, and we need to subtract the total cost of the bagels from this amount.
#    - Money left = Initial amount - Total cost
#    - Money left = 23 - 15 = $8

# Therefore, Olivia has $8 left after buying the bagels. The answer is $8.
# To find out how much money Olivia has left after buying the bagels, we can follow these steps:

# 1. **Determine the cost of the bagels**: Olivia bought 5 bagels, and each bagel costs $3. So, we calculate the total cost:
#    \[
#    \text{Total cost} = 5 \times 3 = 15 \text{ dollars}
#    \]

# 2. **Calculate how much money Olivia has left**: Olivia started with $23. After spending $15 on the bagels, we subtract the cost from her initial amount:
#    \[
#    \text{Money left} = 23 - 15 = 8 \text{ dollars}
#    \]

# Therefore, Olivia has $8 left. The answer is 8.
# To find out how much money Olivia has left, we can follow these steps:

# 1. **Determine the cost of the bagels**: Olivia bought 5 bagels, and each bagel costs $3. So, we calculate the total cost:
#    \[
#    5 \text{ bagels} \times 3 \text{ dollars/bagel} = 15 \text{ dollars}
#    \]

# 2. **Subtract the cost from her initial amount**: Olivia started with $23. Now we subtract the total cost of the bagels from this amount:
#    \[
#    23 \text{ dollars} - 15 \text{ dollars} = 8 \text{ dollars}
#    \]

# 3. **Conclusion**: After buying the bagels, Olivia has $8 left.

# The answer is $8.
# To find out how much money Olivia has left after buying the bagels, let's go through the steps:

# 1. **Determine how much Olivia spent on the bagels.**
#    Olivia bought 5 bagels for $3 each.
#    To find the total cost of the bagels, we multiply the number of bagels by the price per bagel:
#    \[
#    5 \text{ bagels} \times 3 \text{ dollars/bagel} = 15 \text{ dollars}
#    \]

# 2. **Calculate how much money Olivia has left after the purchase.**
#    Olivia started with $23 and spent $15 on the bagels.
#    To find out how much money she has left, we subtract the amount spent from her initial amount:
#    \[
#    23 \text{ dollars} - 15 \text{ dollars} = 8 \text{ dollars}
#    \]

# Therefore, Olivia has $8 left. The answer is $8.
# To find out how much money Olivia has left after buying the bagels, we can follow these steps:

# 1. **Determine the cost of the bagels**: Olivia bought 5 bagels for $3 each.
#    - So, the total cost for the bagels is:
#    \[
#    5 \text{ bagels} \times 3 \text{ dollars/bagel} = 15 \text{ dollars}
#    \]

# 2. **Calculate how much money Olivia has left**: Olivia started with $23, and now we subtract the cost of the bagels from her initial amount.
#    - The calculation is:
#    \[
#    23 \text{ dollars} - 15 \text{ dollars} = 8 \text{ dollars}
#    \]

# 3. **Conclusion**: After buying the bagels, Olivia has $8 left.

# The answer is $8.
