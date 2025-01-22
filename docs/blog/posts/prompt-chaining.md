---
title: Prompt Chaining in AI Development
description: >
  Prompt chaining is a way to simplify large, complex prompts by breaking them down into smaller prompts, each making their own separate LLM call.
authors:
  - willbakst
categories:
  - Tips & Inspiration
date: 2024-06-05
slug: prompt-chaining
---

# Prompt Chaining in AI Development

Prompt chaining is a way to sequence LLM calls (and their prompts) by using the output of the last call as input to the next, to guide an LLM to produce more useful answers than if it had been prompted only once.

By treating the entire chain of calls and prompts as part of a larger request to arrive at an ultimate response, you’re able to refine and steer the intermediate calls and responses at each step to achieve a better result.

Prompt chaining allows you to manage what may start out as a large, unwieldy prompt, whose implicitly defined subtasks and details can throw off language models and result in unsatisfying responses. **This is because LLMs lose focus when asked to process different ideas thrown together.** They can misread relationships between different instructions and incompletely execute them.

<!-- more -->

Such misreadings can also cascade as downstream errors given that LLMs generate text token by token.

We even see this in Chain-of-Thought prompting (CoT) sometimes. Though this style of prompting does a reasonably good job at decomposing tasks into smaller ones, it nonetheless generates the entire output on the fly in a single call—with no intermediate steps.

**This gives you no granular control over the flow:** What if you want to prompt engineer around the attributes of a single variable in the middle of a sequence?

That’s why prompt chaining is suitable for some situations. In this article, we give you a full picture of what prompt chains do. We also show ways of implementing chains using [Mirascope](https://github.com/mirascope/mirascope), our own Python toolkit for building with language models, along with do’s and don’ts for chaining LLM calls.

## A Brief Use Case

Imagine asking an LLM to generate a detailed travel itinerary for a week-long trip across Europe. You supply it with details like starting date, countries of interest, and duration of visit. You want it to give details on flight suggestions, hotel recommendations, and local attractions.

Feeding all this into the language model in one go might not produce the output you’re looking for. It might struggle to prioritize and accurately fulfill each request (whether explicitly or implicitly stated), resulting in an incomplete or unsatisfying itinerary. You might end up refining the prompt and resubmitting it until you’re satisfied with the answer.

To implement prompt chaining, you could break down the main prompt into smaller, separate prompts, each with their own call:

1. “Suggest popular travel destinations in Europe for a week-long trip:” the LLM responds with a list of destinations.
2. “What are good flight options from [starting city] to [chosen destination]:” it responds with a list of flights at different dates and times.
3. “Recommend highly rated hotels in [chosen destination] arriving on [date] for a week-long stay:” it responds with a list of hotel options, and so on.

Smaller prompts and calls are more manageable and allow the model to focus on the details of each individual task, resulting in responses that are likely to be more thorough and accurate than if you had just sent all the details at once.

## Types of Prompt Chains

Although most of the literature concerning chaining focuses on sequential prompting, it’s possible to work with other configurations of prompt chains.

In this section, we briefly describe each of the other prompt engineering techniques before returning to mainly discussing sequential prompts in the rest of this article.

- Sequential prompts
- Parallel prompts
- Conditional prompts
- Recursive prompts

**Note:** Although different prompt types are individually described below, a powerful technique is to combine these as needed in your code.

### Sequential Prompts

These are straightforward in that the chain uses the output of the call from the previous step as input to the next to build a more complex and refined output.

In the sequential prompt below, `recommend_recipe()` calls `select_chef()`, whose output is used for its own response.

```python
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template("Name a chef who is really good at cooking {food_type} food")
def select_chef(food_type: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Imagine that you are chef {chef}.
    Recommend a {food_type} recipe using {ingredient}.
    """
)
def recommend_recipe(food_type: str, ingredient: str) -> openai.OpenAIDynamicConfig:
    return {"computed_fields": {"chef": select_chef(food_type=food_type)}}


print(recommend_recipe(food_type="Japanese", ingredient="apples"))
```

### Parallel Prompts

With parallel prompts, multiple prompts are executed simultaneously, often using the same initial input. The outputs of these parallel prompts can be combined or processed further in subsequent steps.

In the code example below, the `chef` and `ingredients` properties are both computed in parallel and independently, as they don’t depend on each other.

```python
# Parallel Execution
import asyncio

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Please identify a chef who is well known for cooking with {ingredient}.
    Respond only with the chef's name.
    """
)
async def select_chef(ingredient: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Given a base ingredient {ingredient}, return a list of complementary ingredients.
    Make sure to exclude the original ingredient from the list, and respond
    only with the list.
    """
)
async def identify_ingredients(ingredient: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    Your task is to recommend a recipe. Pretend that you are chef {chef}.

    USER:
    Recommend recipes that use the following ingredients:
    {ingredients}
    """
)
async def recommend_recipe(ingredient: str) -> openai.OpenAIDynamicConfig:
    chef, ingredients = await asyncio.gather(
        select_chef(ingredient), identify_ingredients(ingredient)
    )
    return {
        "computed_fields": {"chef": chef, "ingredients": ingredients}
    }


async def recommend_recipe_parallel_chaining(ingredient: str):
    return await recommend_recipe(ingredient=ingredient)


print(asyncio.run(recommend_recipe_parallel_chaining(ingredient="apples")))
```

### Conditional Prompts

Conditional prompts dynamically adjust their prompt queries based on specific conditions or criteria. This involves using conditional logic to modify parts of the prompt template depending on the input data or the results of intermediate steps.

Below, the `conditional_review_prompt` computed field checks the sentiment of the review and returns a different string based on whether the sentiment is positive or negative, which then dynamically adjusts the prompt template used in `response_to_review` method.

```python
# Conditional Prompt
from enum import Enum

from mirascope.core import openai, prompt_template


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


@openai.call(model="gpt-4o-mini", response_model=Sentiment)
@prompt_template("Is the following review positive or negative? {review}")
def classify_sentiment(review: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    Your task is to respond to a review.
    The review has been identified as {sentiment}.

    USER: Write a {conditional_review_prompt} for the following review: {review}
    """
)
def respond_to_review(review: str) -> openai.OpenAIDynamicConfig:
    sentiment = classify_sentiment(review)
    conditional_review_prompt = (
        "thank you response for the review"
        if sentiment == Sentiment.POSITIVE
        else "apologetic response addressing the review"
    )
    return {
        "computed_fields": {
            "sentiment": sentiment,
            "conditional_review_prompt": conditional_review_prompt,
        }
    }




positive_response = respond_to_review(
    review="This tool is awesome because it's so flexible!"
)
print(positive_response)
# > Thank you for your wonderful review! We’re thrilled to hear ...
print(positive_response.user_message_param)
# > {'content': "Write a thank you response for the review for the following review: This tool is awesome because it's so flexible!", 'role': 'user'}

negative_response = respond_to_review(
    review="This product is terrible and too expensive!"
)
print(negative_response)
# > Thank you for sharing your feedback with us. We're truly sorry to hear ...
print(negative_response.user_message_param)
# > {'content': 'Write a apologetic response addressing the review for the following review: This product is terrible and too expensive!', 'role': 'user'}
```

### Iterative Chaining (Recursive Prompts)

Iterative chaining involves a kind of automation in the form of a repeating loop where a prompt calls itself or another prompt in a loop-like structure. This is useful for tasks that require iteration, such as refining outputs or handling multi-step processes that need repeated evaluation.

In the code below, the `rewrite_iteratively` function takes the initial summary of the first prompt to fine-tune it through iterative feedback and rewriting. Each iteration's output becomes the input for the next iteration, and this process is controlled by the `depth` parameter.

```python
# Recursive Prompt
from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


class SummaryFeedback(BaseModel):
    """Feedback on summary with a critique and review rewrite based on said critique."""

    critique: str = Field(..., description="The critique of the summary.")
    rewritten_summary: str = Field(
        ...,
        description="A rewritten summary that takes the critique into account.",
    )


@openai.call(model="gpt-4o-mini")
@prompt_template("Summarize the following text into one sentence: {original_text}")
def summarize(original_text: str): ...


@openai.call(model="gpt-4o-mini", response_model=SummaryFeedback)
@prompt_template(
    """
    Original Text: {original_text}
    Summary: {summary}

    Critique the summary of the original text.
    Then rewrite the summary based on the critique. It must be one sentence.
    """
)
def resummarize(original_text: str, summary: str): ...


def rewrite_iteratively(original_text: str, depth=2):
    summary = summarize(original_text=original_text).content
    for _ in range(depth):
        feedback = resummarize(original_text=original_text, summary=summary)
        summary = feedback.rewritten_summary
    return summary


original_text = """
In the heart of a dense forest, a boy named Timmy pitched his first tent, fumbling with the poles and pegs.
His grandfather, a seasoned camper, guided him patiently, their bond strengthening with each knot tied.
As night fell, they sat by a crackling fire, roasting marshmallows and sharing tales of old adventures.
Timmy marveled at the star-studded sky, feeling a sense of wonder he'd never known.
By morning, the forest had transformed him, instilling a love for the wild that would last a lifetime.
"""

print(rewrite_iteratively(original_text=original_text))
# > In a dense forest, clumsy but eager Timmy, with his grandfather's patient guidance, pitched his first tent, roasted marshmallows by a crackling fire while sharing stories, and gazed at the starry sky, igniting a profound sense of wonder and a lifelong love for nature.
```

## Getting Started with Prompt Chaining, with Examples

Many frameworks offer dedicated chaining functionality, such as LangChain Expression Language (LCEL), which is a declarative language for composing chains.

As its name suggests, [LangChain](https://mirascope.com/blog/langchain-alternatives) was created with chaining in mind and offers specialized classes and abstractions for accomplishing sequences of LLM calls.

You typically assemble chains in LCEL using its pipe operator (`|`), along with classes like `Runnable` and `SequentialChain`. LCEL chains generally have this format:

```python
chain = prompt | model | output_parser
```

LCEL works well with simpler prompts, offering a compact syntax with straightforward flows via the pipe moderator.

But when building more complex chains, we found it challenging to debug errors and follow pipeline operations in detail. For example, with LCEL we always had to use an object that fit into it, so we couldn’t just code as we normally would.

In particular, we found `RunnablePassthrough`, an object that forwards input data without changes through a chain, to be unnecessary and to actually hinder building complex prompts with parallel sub chains. It’s more of an afterthought to solve a problem that LangChain itself created with LCEL. If you do things in a Pythonic way like Mirascope, you don’t need additional classes or structures to pass information through a chain—you simply always have access to it like you should.

Due to the complexity of [working with such frameworks](https://mirascope.com/blog/engineers-should-handle-prompting-llms) we designed Mirascope so you can build pipelines using the Python syntax you already know, rather than having to learn new structures.

Mirascope lets you build prompt chains using either Python properties or functions, as explained below.

### Chaining Prompts Using Computed Fields in Mirascope

Chaining prompts with computed fields means using Mirascope’s dynamic configuration to include the output of a previous call as input in another call, as in the example below:

```python
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Name a scientist who is known for their work in {field_of_study}.
    Give me just the name.
    """
)
def select_scientist(field_of_study: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    Imagine that you are {scientist}.
    Your task is to explain a theory that you, {scientist}, are famous for.

    USER:
    Explain the theory related to {topic}.
    """
)
def explain_theory(field_of_study: str, topic: str) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "scientist": select_scientist(field_of_study=field_of_study)
        }
    }


response = explain_theory(field_of_study="physics", topic="theory of relativity")
print(response)
# > The theory of relativity, developed by Albert Einstein, is a fundamental theory in physics ...
```

By using `@computed_field`, the response’s dump includes the output at every step of the chain:

```python
print(response.model_dump())
# {
#     "metadata": {},
#     "response": {
#         "id": "chatcmpl-9tih8MgTrniWETStrWiLPZYj5riT4",
#         "choices": [
#             {
#                 "finish_reason": "stop",
#                 "index": 0,
#                 "logprobs": None,
#                 "message": {
#                     "content": 'Certainly! The theory of relativity is actually composed of two interrelated theories: special relativity and general relativity.\n\n1. **Special Relativity (1905)**:\nThis theory revolutionizes our understanding of space and time. The core of special relativity is encapsulated in two postulates:\n\n   - **The Laws of Physics are the same for all observers in uniform motion**: This means that whether you are at rest or moving at a constant velocity, the laws of physics, such as Maxwell\'s equations for electromagnetism, apply equally.\n   \n   - **The speed of light in a vacuum is constant for all observers**, regardless of their relative motion. This means that no matter how fast you are moving towards or away from a light source, light will always travel at the same speed of approximately 299,792 kilometers per second (about 186,282 miles per second).\n\nOne of the profound implications of special relativity is the concept of time dilation. This means that time does not pass at the same rate for everyone; the faster an object moves through space, the slower it moves through time as observed from a stationary frame of reference. Another key result is the famous equation \\(E=mc^2\\), which describes the equivalence of mass (m) and energy (E), with \\(c\\) being the speed of light. This indicates that a small amount of mass can be converted into a large amount of energy.\n\n2. **General Relativity (1915)**:\nWhile special relativity deals with flat spacetime and non-accelerating frames, general relativity extends these principles to include gravity and accelerating frames. The central idea of general relativity is that gravity is not a force in the traditional sense but rather a curvature of spacetime caused by mass and energy. \n\nAccording to general relativity, massive objects like planets and stars warp the fabric of spacetime around them, effectively creating a "gravitational well." Objects moving through this curved spacetime will follow paths determined by that curvature. This can be visualized as a heavy ball placed on a rubber sheet causing the sheet to deform. Smaller objects placed on the sheet will roll towards the heavy ball, analogous to how planets orbit stars due to the curvature of spacetime.\n\nGeneral relativity also predicts phenomena such as the bending of light around massive objects (gravitational lensing), the existence of black holes, and the expansion of the universe, all of which have been confirmed by various observations and experiments.\n\nTogether, the theories of relativity have profoundly changed how we understand the universe, challenging our intuitions about time, space, and gravity, and paving the way for modern physics.',
#                     "role": "assistant",
#                     "function_call": None,
#                     "tool_calls": None,
#                     "refusal": None,
#                 },
#             }
#         ],
#         "created": 1723066874,
#         "model": "gpt-4o-mini-2024-07-18",
#         "object": "chat.completion",
#         "service_tier": None,
#         "system_fingerprint": "fp_48196bc67a",
#         "usage": {"completion_tokens": 538, "prompt_tokens": 45, "total_tokens": 583},
#     },
#     "tool_types": [],
#     "prompt_template": "\n    SYSTEM:\n    Imagine that you are {scientist}.\n    Your task is to explain a theory that you, {scientist}, are famous for.\n\n    USER:\n    Explain the theory related to {topic}.\n    ",
#     "fn_args": {
#         "field_of_study": "physics",
#         "topic": "theory of relativity",
#         "scientist": {
#             "metadata": {},
#             "response": {
#                 "id": "chatcmpl-9tih8UOr2dIpQkzQq8vW5adAuDaKx",
#                 "choices": [
#                     {
#                         "finish_reason": "stop",
#                         "index": 0,
#                         "logprobs": None,
#                         "message": {
#                             "content": "Albert Einstein",
#                             "role": "assistant",
#                             "function_call": None,
#                             "tool_calls": None,
#                             "refusal": None,
#                         },
#                     }
#                 ],
#                 "created": 1723066874,
#                 "model": "gpt-4o-mini-2024-07-18",
#                 "object": "chat.completion",
#                 "service_tier": None,
#                 "system_fingerprint": "fp_48196bc67a",
#                 "usage": {
#                     "completion_tokens": 2,
#                     "prompt_tokens": 25,
#                     "total_tokens": 27,
#                 },
#             },
#             "tool_types": [],
#             "prompt_template": "\n    Name a scientist who is known for their work in {field_of_study}.\n    Give me just the name.\n    ",
#             "fn_args": {"field_of_study": "physics"},
#             "dynamic_config": None,
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": "Name a scientist who is known for their work in physics.\nGive me just the name.",
#                 }
#             ],
#             "call_params": {},
#             "call_kwargs": {
#                 "model": "gpt-4o-mini",
#                 "messages": [
#                     {
#                         "role": "user",
#                         "content": "Name a scientist who is known for their work in physics.\nGive me just the name.",
#                     }
#                 ],
#             },
#             "user_message_param": {
#                 "content": "Name a scientist who is known for their work in physics.\nGive me just the name.",
#                 "role": "user",
#             },
#             "start_time": 1723066873977.3618,
#             "end_time": 1723066874552.072,
#             "message_param": {
#                 "content": "Albert Einstein",
#                 "role": "assistant",
#                 "tool_calls": None,
#                 "refusal": None,
#             },
#             "tools": None,
#             "tool": None,
#         },
#     },
#     "dynamic_config": {
#         "computed_fields": {
#             "scientist": {
#                 "metadata": {},
#                 "response": {
#                     "id": "chatcmpl-9tih8UOr2dIpQkzQq8vW5adAuDaKx",
#                     "choices": [
#                         {
#                             "finish_reason": "stop",
#                             "index": 0,
#                             "logprobs": None,
#                             "message": {
#                                 "content": "Albert Einstein",
#                                 "role": "assistant",
#                                 "function_call": None,
#                                 "tool_calls": None,
#                                 "refusal": None,
#                             },
#                         }
#                     ],
#                     "created": 1723066874,
#                     "model": "gpt-4o-mini-2024-07-18",
#                     "object": "chat.completion",
#                     "service_tier": None,
#                     "system_fingerprint": "fp_48196bc67a",
#                     "usage": {
#                         "completion_tokens": 2,
#                         "prompt_tokens": 25,
#                         "total_tokens": 27,
#                     },
#                 },
#                 "tool_types": [],
#                 "prompt_template": "\n    Name a scientist who is known for their work in {field_of_study}.\n    Give me just the name.\n    ",
#                 "fn_args": {"field_of_study": "physics"},
#                 "dynamic_config": None,
#                 "messages": [
#                     {
#                         "role": "user",
#                         "content": "Name a scientist who is known for their work in physics.\nGive me just the name.",
#                     }
#                 ],
#                 "call_params": {},
#                 "call_kwargs": {
#                     "model": "gpt-4o-mini",
#                     "messages": [
#                         {
#                             "role": "user",
#                             "content": "Name a scientist who is known for their work in physics.\nGive me just the name.",
#                         }
#                     ],
#                 },
#                 "user_message_param": {
#                     "content": "Name a scientist who is known for their work in physics.\nGive me just the name.",
#                     "role": "user",
#                 },
#                 "start_time": 1723066873977.3618,
#                 "end_time": 1723066874552.072,
#                 "message_param": {
#                     "content": "Albert Einstein",
#                     "role": "assistant",
#                     "tool_calls": None,
#                     "refusal": None,
#                 },
#                 "tools": None,
#                 "tool": None,
#             }
#         }
#     },
#     "messages": [
#         {
#             "role": "system",
#             "content": "Imagine that you are Albert Einstein.\nYour task is to explain a theory that you, Albert Einstein, are famous for.",
#         },
#         {
#             "role": "user",
#             "content": "Explain the theory related to theory of relativity.",
#         },
#     ],
#     "call_params": {},
#     "call_kwargs": {
#         "model": "gpt-4o-mini",
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "Imagine that you are Albert Einstein.\nYour task is to explain a theory that you, Albert Einstein, are famous for.",
#             },
#             {
#                 "role": "user",
#                 "content": "Explain the theory related to theory of relativity.",
#             },
#         ],
#     },
#     "user_message_param": {
#         "content": "Explain the theory related to theory of relativity.",
#         "role": "user",
#     },
#     "start_time": 1723066874557.961,
#     "end_time": 1723066886474.831,
#     "message_param": {
#         "content": 'Certainly! The theory of relativity is actually composed of two interrelated theories: special relativity and general relativity.\n\n1. **Special Relativity (1905)**:\nThis theory revolutionizes our understanding of space and time. The core of special relativity is encapsulated in two postulates:\n\n   - **The Laws of Physics are the same for all observers in uniform motion**: This means that whether you are at rest or moving at a constant velocity, the laws of physics, such as Maxwell\'s equations for electromagnetism, apply equally.\n   \n   - **The speed of light in a vacuum is constant for all observers**, regardless of their relative motion. This means that no matter how fast you are moving towards or away from a light source, light will always travel at the same speed of approximately 299,792 kilometers per second (about 186,282 miles per second).\n\nOne of the profound implications of special relativity is the concept of time dilation. This means that time does not pass at the same rate for everyone; the faster an object moves through space, the slower it moves through time as observed from a stationary frame of reference. Another key result is the famous equation \\(E=mc^2\\), which describes the equivalence of mass (m) and energy (E), with \\(c\\) being the speed of light. This indicates that a small amount of mass can be converted into a large amount of energy.\n\n2. **General Relativity (1915)**:\nWhile special relativity deals with flat spacetime and non-accelerating frames, general relativity extends these principles to include gravity and accelerating frames. The central idea of general relativity is that gravity is not a force in the traditional sense but rather a curvature of spacetime caused by mass and energy. \n\nAccording to general relativity, massive objects like planets and stars warp the fabric of spacetime around them, effectively creating a "gravitational well." Objects moving through this curved spacetime will follow paths determined by that curvature. This can be visualized as a heavy ball placed on a rubber sheet causing the sheet to deform. Smaller objects placed on the sheet will roll towards the heavy ball, analogous to how planets orbit stars due to the curvature of spacetime.\n\nGeneral relativity also predicts phenomena such as the bending of light around massive objects (gravitational lensing), the existence of black holes, and the expansion of the universe, all of which have been confirmed by various observations and experiments.\n\nTogether, the theories of relativity have profoundly changed how we understand the universe, challenging our intuitions about time, space, and gravity, and paving the way for modern physics.',
#         "role": "assistant",
#         "tool_calls": None,
#         "refusal": None,
#     },
#     "tools": None,
#     "tool": None,
# }
```

We generally recommend building with computed fields:

- Your pipelines will be more readable than with functions, as the flow of data and dependencies will be clear.
- Once defined, properties can be reused multiple times.
- Properties are evaluated only when accessed, which can be efficient if certain steps in the chain are conditionally required or reused multiple times.
- Using properties keeps the logic encapsulated within the class, making it easier to manage and debug. Each property represents a distinct step in the chain, and the dependencies are explicitly defined.

### Chaining Prompts Using Functions in Mirascope

You can alternatively use functions rather than properties to chain prompts, where you straightforwardly pass the output from one call to the next. Functions offer a simple way to build chains but lack the efficiency of being able to cache call outputs and colocate with one prompt all inputs along the chain.

```python
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Name a scientist who is known for their work in {field_of_study}.
    Give me just the name.
    """
)
def select_scientist(field_of_study: str): ...


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    Imagine that you are {scientist}.
    Your task is to explain a theory that you, {scientist}, are famous for.

    USER:
    Explain the theory related to {topic}.
    """
)
def explain_theory(scientist: str, topic: str): ...


def explain_theory_as_scientist(field_of_study: str, topic: str):
    scientist = select_scientist(field_of_study=field_of_study).content
    explanation = explain_theory(scientist=scientist, topic=topic)
    return explanation


response = explain_theory_as_scientist(
    field_of_study="physics", topic="theory of relativity"
)
print(response)
# > Certainly! Here's an explanation of the theory of relativity: ...
```

When using functions for prompt chaining, the results of intermediate steps may not be evident. When dumping the results for these example functions, we see that `field_of_study=”physics”` doesn’t appear, which means you’d need to log every call along the chain to get full transparency on model outputs.

```python
print(response.model_dump())
# {
#     "metadata": {},
#     "response": {
#         "id": "chatcmpl-9tipx51yKYmtaleyNltoZEd4h2iou",
#         "choices": [
#             {
#                 "finish_reason": "stop",
#                 "index": 0,
#                 "logprobs": None,
#                 "message": {
#                     "content": "Ah, the theory that many people associate with my work is the theory of relativity, which is actually comprised of two parts: special relativity and general relativity. Let me explain each component.\n\n**Special Relativity (1905)**: This theory fundamentally changed our understanding of space and time. At its core, special relativity asserts two key principles:\n\n1. **The Principle of Relativity**: The laws of physics are the same in all inertial frames of reference, meaning that whether you are at rest or moving at a constant speed, the laws governing physical phenomena do not change.\n\n2. **The Constancy of the Speed of Light**: Light travels at a constant speed (approximately 299,792 kilometers per second or about 186,282 miles per second) in a vacuum, regardless of the motion of the source or the observer. \n\nFrom these postulates, we can derive several intriguing concepts, including time dilation (time moves slower for an object in motion relative to a stationary observer) and length contraction (objects in motion are measured to be shorter in the direction of motion by stationary observers). \n\nPerhaps the most famous equation that stems from special relativity is \\( E = mc^2 \\), which posits that energy (E) is equivalent to mass (m) multiplied by the square of the speed of light (c). This equation implies that a small amount of mass can be converted into a large amount of energy, a principle that has profound implications for both theoretical physics and practical applications, such as nuclear energy.\n\n**General Relativity (1915)**: This theory extends the principles of special relativity to include gravity. In general relativity, I proposed that gravity is not a force in the traditional sense but rather a curvature of spacetime caused by the presence of mass. According to this view, massive objects (like planets and stars) warp the fabric of spacetime around them, and this curvature affects the motion of other objects, which we perceive as the force of gravity.\n\nThis theory also leads to predictions such as the bending of light around massive objects (gravitational lensing), the time dilation effects in strong gravitational fields (where time runs slower closer to a massive body), and the existence of phenomena such as black holes and gravitational waves.\n\nIn essence, the theory of relativity has transformed our understanding of the universe, challenging classical notions of time, space, and gravity, and continues to influence modern physics and cosmology profoundly.",
#                     "role": "assistant",
#                     "function_call": None,
#                     "tool_calls": None,
#                     "refusal": None,
#                 },
#             }
#         ],
#         "created": 1723067421,
#         "model": "gpt-4o-mini-2024-07-18",
#         "object": "chat.completion",
#         "service_tier": None,
#         "system_fingerprint": "fp_48196bc67a",
#         "usage": {"completion_tokens": 497, "prompt_tokens": 45, "total_tokens": 542},
#     },
#     "tool_types": [],
#     "prompt_template": "\n    SYSTEM:\n    Imagine that you are {scientist}.\n    Your task is to explain a theory that you, {scientist}, are famous for.\n\n    USER:\n    Explain the theory related to {topic}.\n    ",
#     "fn_args": {"scientist": "Albert Einstein", "topic": "theory of relativity"},
#     "dynamic_config": None,
#     "messages": [
#         {
#             "role": "system",
#             "content": "Imagine that you are Albert Einstein.\nYour task is to explain a theory that you, Albert Einstein, are famous for.",
#         },
#         {
#             "role": "user",
#             "content": "Explain the theory related to theory of relativity.",
#         },
#     ],
#     "call_params": {},
#     "call_kwargs": {
#         "model": "gpt-4o-mini",
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "Imagine that you are Albert Einstein.\nYour task is to explain a theory that you, Albert Einstein, are famous for.",
#             },
#             {
#                 "role": "user",
#                 "content": "Explain the theory related to theory of relativity.",
#             },
#         ],
#     },
#     "user_message_param": {
#         "content": "Explain the theory related to theory of relativity.",
#         "role": "user",
#     },
#     "start_time": 1723067421089.7852,
#     "end_time": 1723067429478.955,
#     "message_param": {
#         "content": "Ah, the theory that many people associate with my work is the theory of relativity, which is actually comprised of two parts: special relativity and general relativity. Let me explain each component.\n\n**Special Relativity (1905)**: This theory fundamentally changed our understanding of space and time. At its core, special relativity asserts two key principles:\n\n1. **The Principle of Relativity**: The laws of physics are the same in all inertial frames of reference, meaning that whether you are at rest or moving at a constant speed, the laws governing physical phenomena do not change.\n\n2. **The Constancy of the Speed of Light**: Light travels at a constant speed (approximately 299,792 kilometers per second or about 186,282 miles per second) in a vacuum, regardless of the motion of the source or the observer. \n\nFrom these postulates, we can derive several intriguing concepts, including time dilation (time moves slower for an object in motion relative to a stationary observer) and length contraction (objects in motion are measured to be shorter in the direction of motion by stationary observers). \n\nPerhaps the most famous equation that stems from special relativity is \\( E = mc^2 \\), which posits that energy (E) is equivalent to mass (m) multiplied by the square of the speed of light (c). This equation implies that a small amount of mass can be converted into a large amount of energy, a principle that has profound implications for both theoretical physics and practical applications, such as nuclear energy.\n\n**General Relativity (1915)**: This theory extends the principles of special relativity to include gravity. In general relativity, I proposed that gravity is not a force in the traditional sense but rather a curvature of spacetime caused by the presence of mass. According to this view, massive objects (like planets and stars) warp the fabric of spacetime around them, and this curvature affects the motion of other objects, which we perceive as the force of gravity.\n\nThis theory also leads to predictions such as the bending of light around massive objects (gravitational lensing), the time dilation effects in strong gravitational fields (where time runs slower closer to a massive body), and the existence of phenomena such as black holes and gravitational waves.\n\nIn essence, the theory of relativity has transformed our understanding of the universe, challenging classical notions of time, space, and gravity, and continues to influence modern physics and cosmology profoundly.",
#         "role": "assistant",
#         "tool_calls": None,
#         "refusal": None,
#     },
#     "tools": None,
#     "tool": None,
# }
```

Functions offer some advantages, however:

- They offer explicit control over the flow of execution, making it easier to implement complex chains where steps might need to be skipped or conditionally executed. This can be more straightforward compared to using properties, as functions allow you to write normal Python scripts with simple conditional logic.
- Functions can be more easily reused across different classes and modules. This is useful if the chaining logic needs to be applied in various contexts or with different classes.

## Downsides of Prompt Chaining

Prompt chaining provides utility in situations where you want to set up pipelines for processing and transforming data step-by-step.

However, there are downsides:

- Each step of the chain needs to be explicitly defined ahead of time in a fixed sequence, which leaves little room for deviation based on runtime conditions or user input beyond what has been predefined. A dynamically generated agent workflow might adapt more flexibly to different conditions at runtime, but with this you also lose granular control over each piece of the chain.

- Prompt chaining isn’t necessarily a cheaper option than alternatives, but it depends on how calls are structured since they’re token based and a chain with two calls may cost the same as a single CoT call if the input and output tokens are the same.

- Speed might also be a downside, as you’ll need to make several requests instead of just one and this can slow down the "real-time" feel of the application. In such cases, you might consider providing feedback to the user, like progress messages, as the chain is executing intermediate steps.

You should balance these considerations when deciding whether to leverage prompt chaining for generative AI in your application.

## Best Practices for Prompt Chaining

Good prompt chaining practices share a lot with best [prompt engineering](https://mirascope.com/blog/prompt-engineering-tools) practices. Here are some recommendations for developing effective prompt chains when using AI models:

### Keep Your Prompts Focused and Specific

Clear and concise prompts minimize misunderstandings by the model. For example, rather than writing, "Tell me something about scientists," a more focused prompt might be, "Name a scientist known for their work in quantum physics."

Each prompt should also perform a specific function and have a single responsibility assigned. This means breaking down complex tasks into smaller, manageable steps where each prompt addresses one aspect of the overall task.

### Manage Data Carefully

Ensure that the format of the desired output of one prompt matches the expected input format of the next prompt to avoid errors. Schemas can easily help you achieve this, and the Mirascope library offers its [`response_model`](https://mirascope.com/learn/response_models) argument, which is built on top of Pydantic, to help you define schemas, extract structured outputs from large language models, and validate those outputs.

For example, if a prompt expects a JSON object with specific fields, ensure the preceding prompt generates data in that exact structure. As well, be prepared to transform data to meet the input requirements of subsequent prompts. This might involve parsing JSON, reformatting strings, or converting data types.

### Optimize for Performance

Use caching like `@functools.lru_cache` whenever feasible to improve performance. We also recommend finding ways to minimize the number of sequential calls by combining steps where possible, which may involve consolidating prompts or rethinking the chain structure to reduce the dependency on intermediate results.

The goal should be to minimize latency for the user experience, but there’s a tradeoff with complexity, as decreasing latency might increase the complexity of individual steps. Developers need to balance the trade-offs between maintaining a clear, manageable chain and optimizing for speed.

## Harness the Efficiency of Python for Prompt Chaining

Mirascope leverages Python for chaining LLM calls, avoiding the need for complex abstractions with steep learning curves, as well as having to master new frameworks.

By keeping things simple, Mirascope lets you work with your data directly, helping you keep your workflows smoother and more intuitive.

Want to learn more? You can find more Mirascope code samples on both our [documentation site](https://mirascope.com) and on [GitHub](https://github.com/mirascope/mirascope/).
