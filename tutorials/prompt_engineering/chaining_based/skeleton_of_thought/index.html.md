# Skeleton of Thought: Enhancing LLM Response Speed

This recipe demonstrates how to implement Skeleton of Thought, a speed-oriented prompt engineering technique.

This recipe demonstrates how to implement the Skeleton of Thought technique using Large Language Models (LLMs) with Mirascope.

<details class="tip">
<summary>Mirascope Concepts Used</summary>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
<li><a href="../../../../learn/response_models/">Response Models</a></li>
</ul>
</details>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p><a href="https://arxiv.org/pdf/2307.15337">Skeleton of Thought</a> is a prompt-engineering technique that is speed-oriented as opposed to the quality of the response. To expedite the response from a model, make an initial call to create a "skeleton" of the problem that outlines its solution in bulletpoints (without further explanations), then make an individual call with each of the subpoints in parallel before reconstructing the answer at the end.</p>
</div>

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
    You're an organizer responsible for only giving the skeleton (not the full content) for answering the question.
    Provide the skeleton in a list of points (numbered 1., 2., 3., etc.) to answer the question. 
    Instead of writing a full sentence, each skeleton point should be very short with only 3∼5 words.
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
    You're responsible for continuing the writing of one and only one point in the overall answer to the following question:

    {query}

    The skeleton of the answer is:

    {skeleton}

    Continue and only continue the writing of point {point_index}. Write it very shortly in 1-2 sentences and do not continue with other points!
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


print(await skeleton_of_thought(query))
```

    Identify distractions by making a list of the things that tend to pull your attention away from the task at hand. Once you know what they are, you can take steps to minimize their impact on your focus.
    Establishing a routine can help improve focus by creating structure and consistency in your daily tasks and priorities. By sticking to a set schedule, you can reduce the likelihood of getting off track and better manage your time and energy.
    Set specific goals by breaking down your tasks into smaller, manageable steps with clear deadlines. This will help you stay on track and maintain focus on what needs to be accomplished.
    4. Practice mindfulness by staying present in the moment and focusing on your breathing to help quiet the mind and improve concentration.
    Take regular breaks to give your mind time to rest and recharge, allowing you to come back to your tasks with renewed focus and energy.


This implementation demonstrates how to use Skeleton of Thought with Mirascope. The `break_into_subpoints` function creates the initial skeleton, and `expand_subpoint` expands each subpoint in parallel. The `skeleton_of_thought` function orchestrates the entire process.

Intermediate Response:



```python
print(break_into_subpoints(query))
```

    subpoints=['Identify distractions', 'Implement time management techniques', 'Practice mindfulness', 'Get enough sleep', 'Stay hydrated', 'Exercise regularly', 'Set clear goals', 'Take short breaks', 'Limit multitasking']


## Benefits and Considerations

The Skeleton of Thought implementation offers several advantages:

1. Improved response speed by parallelizing the expansion of subpoints.
2. Enhanced structure in responses, making them easier to read and understand.
3. Potential for better performance on complex queries that benefit from a structured approach.

When implementing this technique, consider:

- Balancing the number of subpoints with the desired response length and complexity.
- Adjusting the prompt for subpoint expansion based on the specific use case or domain.
- Implementing error handling and retries to ensure robustness in production environments.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Content Creation</b>: Use Skeleton of Thought to quickly generate outlines for articles or blog posts.</li>
<li><b>Project Planning</b>: Rapidly break down complex projects into manageable tasks and subtasks.</li>
<li><b>Educational Materials</b>: Create structured lesson plans or study guides efficiently.</li>
<li><b>Technical Documentation</b>: Generate quick, well-structured documentation outlines for software or products.</li>
<li><b>Problem-Solving</b>: Break down complex problems into smaller, more manageable components for analysis.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Customizing the skeleton generation prompt to fit your domain-specific needs.
- Experimenting with different LLM models for skeleton generation and subpoint expansion to optimize for speed and quality.
- Implementing a feedback loop to refine the skeleton based on the quality of expanded subpoints.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the Skeleton of Thought technique to enhance your LLM's response speed and structure across a wide range of applications.
