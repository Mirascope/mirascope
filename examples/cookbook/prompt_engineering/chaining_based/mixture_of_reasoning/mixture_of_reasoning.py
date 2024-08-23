from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Answer this question, thinking step by step.
    {query}
    """
)
def cot_call(query: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    {query}
    It's very important to my career.
    """
)
def emotion_prompting_call(query: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    {query}
    Rephrase and expand the question, and respond.
    """
)
def rar_call(query: str): ...


class BestResponse(BaseModel):
    best_response: str = Field(
        ..., description="The best response of the options given, verbatim"
    )
    reasoning: str = Field(
        ...,
        description="""A short description of why this is the best response to
        the query, along with reasons why the other answers were worse.""",
    )


@openai.call(model="gpt-4o-mini", response_model=BestResponse)
@prompt_template(
    """
    Here is a query: {query}

    Evaluate the following responses from LLMs and decide which one
    is the best based on correctness, fulfillment of the query, and clarity:

    Response 1:
    {cot_response}

    Response 2:
    {emotion_prompting_response}

    Response 3:
    {rar_response}
    """
)
def mixture_of_reasoning(query: str) -> openai.OpenAIDynamicConfig:
    cot_response = cot_call(query=query)
    emotion_prompting_response = emotion_prompting_call(query=query)
    rar_response = rar_call(query=query)
    # Uncomment to see intermediate responses
    # print(cot_response)
    # print(emotion_prompting_response)
    # print(rar_response)

    return {
        "computed_fields": {
            "cot_response": cot_response,
            "emotion_prompting_response": emotion_prompting_response,
            "rar_response": rar_response,
        }
    }


prompt = """What are the side lengths of a rectangle with area 8 and perimeter 12?"""

best_response = mixture_of_reasoning(prompt)
print(best_response.best_response)
# > Response 2: The best response is Response 2. It directly and correctly solves the system of equations to find the side lengths of the rectangle with the area 8 and perimeter 12. It provides clear steps and demonstrates the correct approach to the problem, yielding the correct result of 2 units by 4 units.

print(best_response.reasoning)
# > Response 1 overcomplicates the solution process by introducing unnecessary steps and expressions. Response 3 contains an error in the calculation and solution steps, providing incorrect side lengths for the rectangle. Response 2 simplifies the equations and solves for the side lengths accurately and concisely, making it the most effective response.

# Intermediate Responses

# cot_response = cot_call(query=query)
# To find the side lengths of a rectangle with area 8 and perimeter 12, we need to denote the length and width of the rectangle as variables. Let's use L for the length and W for the width.

# Step 1: Identify the formulas for the area and perimeter of a rectangle.
# Area of a rectangle = length x width
# Perimeter of a rectangle = 2(length + width)

# Step 2: Given that the area of the rectangle is 8, set up the equation using the formula for the area.
# L x W = 8

# Step 3: Given that the perimeter of the rectangle is 12, set up the equation using the formula for the perimeter.
# 2(L + W) = 12
# L + W = 6

# Step 4: We now have a system of equations:
# L x W = 8
# L + W = 6

# Step 5: Solve the system of equations simultaneously to find the values of L and W. Let's substitute one of the variables to solve for the other:
# L = 6 - W

# Step 6: Substitute L = 6 - W into the equation L x W = 8:
# (6 - W) x W = 8
# 6W - W^2 = 8
# W^2 - 6W + 8 = 0

# Step 7: Solve the quadratic equation for W. Factoring or using the quadratic formula will give you the values of W.

# Step 8: Once you have the value(s) of W, substitute back into L = 6 - W to find the corresponding value(s) of L.

# Step 9: Check the solutions to ensure they satisfy the conditions given in the question.

# By following these steps, you can determine the side lengths of the rectangle with area 8 and perimeter 12.


# emotion_prompting_response = emotion_prompting_call(query=query)
# Let's denote the length of the rectangle as L and the width as W.

# The area of a rectangle is given by the formula Area = Length x Width. So in this case, we have that LW = 8.

# The perimeter of a rectangle is given by the formula Perimeter = 2(Length + Width). So in this case, we have that 2(L + W) = 12.

# We are looking to solve the system of equations:

# LW = 8
# 2(L + W) = 12

# From the first equation, we can rewrite it as W = 8/L.

# Substitute this into the second equation:

# 2(L + 8/L) = 12
# 2L + 16/L = 12
# 2L^2 + 16 = 12L
# 2L^2 - 12L + 16 = 0

# Solving this quadratic equation, we get L = 2 or L = 8.

# Therefore, the possible sides of the rectangle are 2 and 4 or 4 and 2.


# rar_response = rar_call(query=query)
# What are the dimensions of a rectangle with an area of 8 square units and a perimeter of 12 units?

# Let's denote the length of the rectangle as L units and the width as W units.
# Given that the area of the rectangle is 8 units², we have the equation:
# L x W = 8

# Also, the perimeter of a rectangle is given by the formula:
# 2L + 2W = 12

# We are asked to find the values of L and W that satisfy both of these equations. Solving these two equations simultaneously, we can find the side lengths of the rectangle. Let's start by substituting L = 8/W into the perimeter equation:

# 2(8/W) + 2W = 12
# 16/W + 2W = 12
# 16 + 2W² = 12W
# 2W² -12W + 16 = 0
# W² - 6W + 8 = 0
# (W-4)(W-2) = 0
# W=4 or W=2

# Therefore, the possible values for W are 4 units or 2 units.
# Substitute W = 4 into L x W = 8:
# L x 4 = 8
# L = 2 units
# So, the dimensions of the rectangle are 2 units by 4 units.
