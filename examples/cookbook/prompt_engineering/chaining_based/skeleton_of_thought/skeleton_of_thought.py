import asyncio

from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


class Skeleton(BaseModel):
    subpoints: list[str] = Field(
        ...,
        description="""The subpoints of the skeleton of the original query.
        Each is 3-5 words and starts with its point index, e.g. 
        1. Some subpoint...""",
    )


@openai.call(model="gpt-3.5-turbo", response_model=Skeleton)
@prompt_template(
    """
    You’re an organizer responsible for only giving the skeleton
    (not the full content) for answering the question.
    Provide the skeleton in a list of points (numbered 1., 2., 3., etc.) to
    answer the question. Instead of writing a full sentence, each skeleton point
    should be very short with only 3∼5 words. Generally, the skeleton should have
    3∼10 points. Now, please provide the skeleton for the following question.
    {query}
    Skeleton:
    """
)
def break_into_subpoints(query: str): ...


@openai.call(model="gpt-3.5-turbo")
@prompt_template(
    """
    You’re responsible for continuing the writing of one and only one point in
    the overall answer to the following question:

    {query}

    The skeleton of the answer is:

    {skeleton}

    Continue and only continue the writing of point {point_index}. Write it very
    shortly in 1-2 sentences and do not continue with other points!
    """
)
async def expand_subpoint(query: str, skeleton: list[str], point_index: int): ...


query = "How can I improve my focus?"


async def skeleton_of_thought(query):
    skeleton = break_into_subpoints(query)
    # Uncomment to see intermediate responses
    # print(skeleton)
    tasks = [
        expand_subpoint(query, skeleton.subpoints, i + 1)
        for i, subpoint in enumerate(skeleton.subpoints)
    ]
    results = await asyncio.gather(*tasks)
    return "\n".join([result.content for result in results])


print(asyncio.run(skeleton_of_thought(query)))
# > 1. Set specific goals: Clearly define what you want to achieve and break down your tasks into manageable steps to stay focused on your objectives.
#   2. Create a schedule: Organize your tasks and allocate specific times to work on them, allowing you to stay on track and prioritize effectively.
#   3. Minimize distractions by turning off notifications, finding a quiet workspace, and setting boundaries with others.
#   4. Taking regular breaks throughout the day can help improve focus by giving your mind a chance to rest and rejuvenate, allowing you to come back to your tasks with renewed energy and clarity.
#   5. Practice mindfulness by being fully present in the moment and focusing on one task at a time to improve your concentration and mental clarity.

# Intermediate Responses

# skeleton = break_into_subpoints(prompt)
# > subpoints=['1. Set specific goals', '2. Create a schedule', '3. Minimize distractions', '4. Take breaks', '5. Practice mindfulness']
