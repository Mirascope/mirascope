# Skeleton of Thought: Enhancing LLM Response Speed

This recipe demonstrates how to implement Skeleton of Thought, a speed-oriented prompt engineering technique.

This recipe demonstrates how to implement the Skeleton of Thought technique using Large Language Models (LLMs) with Mirascope.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../../learn/prompts.md)
    - [Calls](../../../learn/calls.md)
    - [Response Models](../../../learn/response_models.md)

!!! note "Background"

    [Skeleton of Thought](https://arxiv.org/pdf/2307.15337) is a prompt-engineering technique that is speed-oriented as opposed to the quality of the response. To expedite the response from a model, make an initial call to create a "skeleton" of the problem that outlines its solution in bulletpoints (without further explanations), then make an individual call with each of the subpoints in parallel before reconstructing the answer at the end.


## Basic Skeleton of Thought Implementation

Let's start with a basic implementation of Skeleton of Thought:

```python
import asyncio

from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field


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
    You're an organizer responsible for only giving the skeleton (not the full \
    content) for answering the question.
    Provide the skeleton in a list of points (numbered 1., 2., 3., etc.) to  answer \
    the question. Instead of writing a full sentence, each skeleton point should be \
    very short with only 3∼5 words.
    Generally, the skeleton should have 3∼10 points.
    Now, please provide the skeleton for the following question.
    {query}
    Skeleton:
    """
)
def break_into_subpoints(query: str): ...


@openai.call(model="gpt-3.5-turbo")
@prompt_template(
    """
    You're responsible for continuing the writing of one and only one point in
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
```

This implementation demonstrates how to use Skeleton of Thought with Mirascope. The `break_into_subpoints` function creates the initial skeleton, and `expand_subpoint` expands each subpoint in parallel. The `skeleton_of_thought` function orchestrates the entire process.

Output:
```
1. Set specific goals: Clearly define what you want to achieve and break down your tasks into manageable steps to stay focused on your objectives.
2. Create a schedule: Organize your tasks and allocate specific times to work on them, allowing you to stay on track and prioritize effectively.
3. Minimize distractions by turning off notifications, finding a quiet workspace, and setting boundaries with others.
4. Taking regular breaks throughout the day can help improve focus by giving your mind a chance to rest and rejuvenate, allowing you to come back to your tasks with renewed energy and clarity.
5. Practice mindfulness by being fully present in the moment and focusing on one task at a time to improve your concentration and mental clarity.
```

Intermediate Response:
```python
skeleton = break_into_subpoints(prompt)
# > subpoints=['1. Set specific goals', '2. Create a schedule', '3. Minimize distractions', '4. Take breaks', '5. Practice mindfulness']
```

## Benefits and Considerations

The Skeleton of Thought implementation offers several advantages:

1. Improved response speed by parallelizing the expansion of subpoints.
2. Enhanced structure in responses, making them easier to read and understand.
3. Potential for better performance on complex queries that benefit from a structured approach.

When implementing this technique, consider:

- Balancing the number of subpoints with the desired response length and complexity.
- Adjusting the prompt for subpoint expansion based on the specific use case or domain.
- Implementing error handling and retries to ensure robustness in production environments.

!!! tip "Additional Real-World Applications"

    - Content Creation: Use Skeleton of Thought to quickly generate outlines for articles or blog posts.
    - Project Planning: Rapidly break down complex projects into manageable tasks and subtasks.
    - Educational Materials: Create structured lesson plans or study guides efficiently.
    - Technical Documentation: Generate quick, well-structured documentation outlines for software or products.
    - Problem-Solving: Break down complex problems into smaller, more manageable components for analysis.

When adapting this recipe to your specific use-case, consider:

- Customizing the skeleton generation prompt to fit your domain-specific needs.
- Experimenting with different LLM models for skeleton generation and subpoint expansion to optimize for speed and quality.
- Implementing a feedback loop to refine the skeleton based on the quality of expanded subpoints.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the Skeleton of Thought technique to enhance your LLM's response speed and structure across a wide range of applications.
