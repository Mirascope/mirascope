import asyncio

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template("{query} Let's think step by step.")
def zero_shot_cot(query: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    USER: Give the concrete prompt (problem) that can generate this answer.
    The problem should contain all basic and necessary information and correspond to the
    answer. The problem can only ask for one result.

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
    Do not list conditions not related to calculations,
    but list all necessary conditions.
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
        description="""Whether the condition is deducible from the list of other
        conditions.""",
    )
    illustration: str = Field(
        ...,
        description="""A quick illustration of the reason the condition is/isn't
        deducible from the list of other conditions.""",
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

    From a mathematical point of view, can this candidate condition be deduced from
    the condition list?
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
    
    From a mathematical point of view, are these two problems asking the same
    thing at the end?
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
    original_conditions, reconstructed_conditions = (
        response.conditions
        for response in await asyncio.gather(
            decompose_query(query), decompose_query(reconstructed_query)
        )
    )

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


async def reverse_cot(query: str):
    cot_response = zero_shot_cot(query=query)
    reconstructed_query_response = reconstruct_query(cot_response.content)
    history = cot_response.messages + reconstructed_query_response.messages
    response = await fine_grained_comparison(
        history=history,
        query=query,
        reconstructed_query=reconstructed_query_response.content,
    )
    # Uncomment to see intermediate values
    # print(response.user_message_param["content"])
    return response


query = """At the trip to the county level scavenger hunt competition 90 people
were required to split into groups for the competition to begin. To break
people up into smaller groups with different leaders 9-person groups were
formed. If 3/5 of the number of groups each had members bring back 2 seashells each
how many seashells did they bring?"""

print(asyncio.run(reverse_cot(query=query)))
# ### Problem Prompt:

# At a county level scavenger hunt competition, there are 90 people who need to be split into smaller groups to begin the competition. For this purpose, 9-person groups are formed. If \( \frac{3}{5} \) of the formed groups had their members each bring back 2 seashells, how many seashells were brought back in total?

# ### Solution Steps:

# 1. **Determine the number of groups formed:**
#    - Total people = 90
#    - Each group consists of 9 people.
#    \[
#    \text{Number of groups} = \frac{90}{9} = 10
#    \]

# 2. **Determine how many groups brought back seashells:**
#    - \( \frac{3}{5} \) of the formed groups brought back seashells.
#    \[
#    \text{Number of groups bringing back seashells} = \frac{3}{5} \times 10 = 6
#    \]

# 3. **Calculate the total number of members in these groups:**
#    - Each of these 6 groups consists of 9 members.
#    \[
#    \text{Total members} = 6 \times 9 = 54
#    \]

# 4. **Calculate the total number of seashells:**
#    - Each member of these groups brought back 2 seashells.
#    \[
#    \text{Total seashells} = 54 \times 2 = 108
#    \]

# Thus, the total number of seashells brought back is **108 seashells**.

# ---

# Thank you for pointing out the need for precision in these scenarios! Your guidance helped clarify the situation effectively.


# Intermediate Steps

# aggregate prompt fed into final call:
# Here are the mistakes and reasons in your answer to the problem.


#             Overlooked Conditions:
#             You have ignored some real conditions:
#             ['There are 90 people who need to be split into groups.', 'Each member of the qualifying groups brought back 2 seashells.']
#             The real problem has the conditions:
#             ['There are 90 people who need to be split into groups.', 'Each group consists of 9 people.', 'Calculate the number of groups formed.', '3/5 of the groups had members who brought back seashells.', 'Each member of the qualifying groups brought back 2 seashells.']
#             You should consider all real conditions in the problem.
#             Here are the detailed reasons:
#             ["The candidate condition refers specifically to '90 people that need to be split into groups', which cannot be directly deduced as the conditions only mention '90 students' without specifying a need for division into groups.", "The candidate condition states 'Each member of the qualifying groups brought back 2 seashells.', which implies that every individual within those groups brought back the seashells. However, the condition list states 'Each student in those groups brought back 2 seashells.', which refers specifically to students. Since the term 'members of the qualifying groups' could include non-students, we cannot deduce that it is true for all members."]

#             Hallucinated Conditions
#             You use some wrong candidate conditions:
#             ['There are 90 students.']
#             They all can not be deduced from the true condition list.
#             The real problem has the conditions:
#             ['There are 90 people who need to be split into groups.', 'Each group consists of 9 people.', 'Calculate the number of groups formed.', '3/5 of the groups had members who brought back seashells.', 'Each member of the qualifying groups brought back 2 seashells.']
#             You should consider all real conditions in the problem.
#             Here are the detailed reasons:
#             ["The candidate condition refers specifically to '90 people that need to be split into groups', which cannot be directly deduced as the conditions only mention '90 students' without specifying a need for division into groups.", "The candidate condition states 'Each member of the qualifying groups brought back 2 seashells.', which implies that every individual within those groups brought back the seashells. However, the condition list states 'Each student in those groups brought back 2 seashells.', which refers specifically to students. Since the term 'members of the qualifying groups' could include non-students, we cannot deduce that it is true for all members."]

#             You misunderstood the question.
#             You think the question is: **Problem Prompt:**

# A school organizes a field trip with 90 students, where they are divided into groups of 9. After the trip, it is found that \( \frac{3}{5} \) of the groups each brought back seashells. If each student in those groups brought back 2 seashells, how many seashells were brought back in total?.
#             But the real question is: At the trip to the county level scavenger hunt competition 90 people
# were required to split into groups for the competition to begin. To break
# people up into smaller groups with different leaders 9-person groups were
# formed. If 3/5 of the number of groups each had members bring back 2 seashells each
# how many seashells did they bring?
#             They are different. You should consider the original question.
# Thank you for your feedback. Based on your comments, I understand that the original problem requires clarity and that I should adhere strictly to the specified conditions. Here is a properly defined problem that incorporates all necessary details and leads to the answer.
