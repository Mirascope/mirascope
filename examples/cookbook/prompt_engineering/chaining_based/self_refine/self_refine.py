from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template("""{query}""")
def call(query: str): ...


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
def evaluate_response(query: str, response: str): ...


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
def generate_new_response(query: str, response: str) -> openai.OpenAIDynamicConfig:
    feedback = evaluate_response(query, response)
    print(feedback)
    return {"computed_fields": {"feedback": feedback}}


def self_refine(query: str, depth: int) -> str:
    response = call(query).content
    # Uncomment to see intermediate responses
    print(response)
    for _ in range(depth):
        response = generate_new_response(query, response).content
        print(response)
    return response


query = """Olivia has $23. She bought five bagels for $3 each.
How much money does she have left?"""
print(self_refine(query, 1))
# > Olivia has $23 initially. She bought five bagels for $3 each. To find out how much she spent in total, we calculate:
#
#   Total cost = Number of bagels × Cost per bagel
#   Total cost = 5 × 3 = $15
#
#  Now, we subtract the total cost from Olivia's initial amount of money to determine how much she has left:
#
#   Money left = Initial amount - Total cost
#   Money left = $23 - $15 = $8
#
#   So, after her purchase of bagels, Olivia has $8 remaining.
#   Olivia has $23 initially. She bought five bagels for $3 each. To find out how much she spent in total, we calculate:
#
#   Total cost = Number of bagels × Cost per bagel
#   Total cost = 5 × 3 = $15
#
#   Now, we subtract the total cost from Olivia's initial amount of money to determine how much she has left:
#
#   Money left = Initial amount - Total cost
#   Money left = $23 - $15 = $8
#
#   So, after her purchase of bagels, Olivia has $8 remaining.


# Intermediate Responses
# response = call(query).content
# Olivia bought five bagels for $3 each. The total cost of the bagels can be calculated as follows:

# Total cost = Number of bagels × Cost per bagel
# Total cost = 5 × 3 = $15

# Now, we subtract the total cost from Olivia's initial amount of money:

# Money left = Initial amount - Total cost
# Money left = $23 - $15 = $8

# So, Olivia has $8 left.

# feedback = evaluate_response(query, response)
# The response to the query is correct in its calculations and reasoning. Here are the points of feedback:

# **Correct Aspects:**
# 1. **Accurate Calculation of Total Cost**: The response correctly identifies that Olivia bought five bagels for $3 each and calculates the total cost as $15 using the formula: Total cost = Number of bagels × Cost per bagel.
# 2. **Correct Subtraction**: The response accurately subtracts the total cost ($15) from Olivia's initial amount ($23) to find the remaining money, resulting in $8.
# 3. **Clear Structure**: The response is well-structured, providing a step-by-step breakdown of the calculations, which makes it easy to follow.

# **Areas for Improvement:**
# - **Clarifying the Context**: While the answer is mathematically correct, adding a brief context or summary at the end ("So, after her purchase of bagels, Olivia has $8 left") would reinforce the conclusion.

# Overall, the response is well done and effectively addresses the query. There are no significant errors, and it demonstrates clarity in problem-solving.

# response = generate_new_response(query, response).content
# Olivia has $23 initially. She bought five bagels for $3 each. To find out how much she spent in total, we calculate:

# Total cost = Number of bagels × Cost per bagel
# Total cost = 5 × 3 = $15

# Now, we subtract the total cost from Olivia's initial amount of money to determine how much she has left:

# Money left = Initial amount - Total cost
# Money left = $23 - $15 = $8

# So, after her purchase of bagels, Olivia has $8 remaining.
# Olivia has $23 initially. She bought five bagels for $3 each. To find out how much she spent in total, we calculate:

# Total cost = Number of bagels × Cost per bagel
# Total cost = 5 × 3 = $15

# Now, we subtract the total cost from Olivia's initial amount of money to determine how much she has left:

# Money left = Initial amount - Total cost
# Money left = $23 - $15 = $8

# So, after her purchase of bagels, Olivia has $8 remaining.
