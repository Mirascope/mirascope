# o1 Style Thinking

In this recipe, we will show how to achieve Chain-of-Thought Reasoning.
This makes LLMs to breakdown the task in multiple steps and generate a coherent output allowing to solve complex tasks in logical steps.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
    Large Language Models (LLMs) are known to generate text that is coherent and fluent. However, they often struggle with tasks that require multi-step reasoning or logical thinking. In this recipe, we will show how to use Mirascope to guide the LLM to break down the task into multiple steps and generate a coherent output.

</p>
</div>


## Setup

To set up our environment, first let's install all of the packages we will use:






```python
!pip install "mirascope[groq]" 
!pip install datetime
```


```python
# Set the appropriate API key for the provider you're using
# Here we are using GROQ_API_KEY

export GROQ_API_KEY="Your API Key"
```

# Without Chain-of-Thought Reasoning

We will begin by showing how a typical LLM performs on a task that requires multi-step reasoning. In this example, we will ask the model to generate a count the number of `s`s in the word `Mississssippi` (Yes it has 7`s`'s). We will use the `llama-3.1-8b-instant` for this example.


```python
from datetime import datetime

from mirascope.core import groq

history: list[dict[str, str]] = []


@groq.call("llama-3.1-8b-instant")
def generate_answer(question: str) -> str:
    return f"Generate an answer to this question: {question}"


def run() -> None:
    question: str = "how many s's in the word mississssippi"
    response: str = generate_answer(question)
    print(f"(User): {question}")
    print(f"(Assistant): {response}")
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response})


run()
```

    (User): how many s's in the word mississssippi
    (Assistant): There are 5 s's in the word "Mississippi".


In this example, the zero-shot method is used to generate the output. The model is not provided with any additional information or context to help it generate the output. The model is only given the input prompt and asked to generate the output.

This is not so effective when there is a logcial task to be performed.

Now let's see how the model performs on this task when it can reason using Chain-of-Thought Reasoning.

# With Chain of Thought Reasoning


```python
from typing import Literal

from mirascope.core import groq
from pydantic import BaseModel, Field


history: list[dict] = []


class COTResult(BaseModel):
    title: str = Field(..., desecription="The title of the step")
    content: str = Field(..., description="The output content of the step")
    next_action: Literal["continue", "final_answer"] = Field(
        ..., description="The next action to take"
    )


@groq.call("llama-3.1-70b-versatile", json_mode=True, response_model=COTResult)
def cot_step(prompt: str, step_number: int, previous_steps: str) -> str:
    return f"""
    You are an expert AI assistant that explains your reasoning step by step.
    For this step, provide a title that describes what you're doing, along with the content.
    Decide if you need another step or if you're ready to give the final answer.

    Guidelines:
    - Use AT MOST 5 steps to derive the answer.
    - Be aware of your limitations as an LLM and what you can and cannot do.
    - In your reasoning, include exploration of alternative answers.
    - Consider you may be wrong, and if you are wrong in your reasoning, where it would be.
    - Fully test all other possibilities.
    - YOU ARE ALLOWED TO BE WRONG. When you say you are re-examining
        - Actually re-examine, and use another approach to do so.
        - Do not just say you are re-examining.

    IMPORTANT: Do not use code blocks or programming examples in your reasoning. Explain your process in plain language.

    This is step number {step_number}.

    Question: {prompt}

    Previous steps:
    {previous_steps}
    """


@groq.call("llama-3.1-70b-versatile")
def final_answer(prompt: str, reasoning: str) -> str:
    return f"""
    Based on the following chain of reasoning, provide a final answer to the question.
    Only provide the text response without any titles or preambles.
    Retain any formatting as instructed by the original prompt, such as exact formatting for free response or multiple choice.

    Question: {prompt}

    Reasoning:
    {reasoning}

    Final Answer:
    """


def generate_cot_response(
    user_query: str,
) -> tuple[list[tuple[str, str, float]], float]:
    steps: list[tuple[str, str, float]] = []
    total_thinking_time: float = 0.0
    step_count: int = 1
    reasoning: str = ""
    previous_steps: str = ""

    while True:
        start_time: datetime = datetime.now()
        cot_result = cot_step(user_query, step_count, previous_steps)
        end_time: datetime = datetime.now()
        thinking_time: float = (end_time - start_time).total_seconds()

        steps.append(
            (
                f"Step {step_count}: {cot_result.title}",
                cot_result.content,
                thinking_time,
            )
        )
        total_thinking_time += thinking_time

        reasoning += f"\n{cot_result.content}\n"
        previous_steps += f"\n{cot_result.content}\n"

        if cot_result.next_action == "final_answer" or step_count >= 5:
            break

        step_count += 1

    # Generate final answer
    start_time = datetime.now()
    final_result: str = final_answer(user_query, reasoning).content
    end_time = datetime.now()
    thinking_time = (end_time - start_time).total_seconds()
    total_thinking_time += thinking_time

    steps.append(("Final Answer", final_result, thinking_time))

    return steps, total_thinking_time


def display_cot_response(
    steps: list[tuple[str, str, float]], total_thinking_time: float
) -> None:
    for title, content, thinking_time in steps:
        print(f"{title}:")
        print(content.strip())
        print(f"**Thinking time: {thinking_time:.2f} seconds**\n")

    print(f"**Total thinking time: {total_thinking_time:.2f} seconds**")


def run() -> None:
    question: str = "How many s's are in the word 'mississssippi'?"
    print("(User):", question)
    # Generate COT response
    steps, total_thinking_time = generate_cot_response(question)
    display_cot_response(steps, total_thinking_time)

    # Add the interaction to the history
    history.append({"role": "user", "content": question})
    history.append(
        {"role": "assistant", "content": steps[-1][1]}
    )  # Add only the final answer to the history


# Run the function

run()
```

    (User): How many s's are in the word 'mississssippi'?
    Step 1: Initial Assessment and Counting:
    To count the number of 's's in the word 'mississssippi', I will first notice that the 's's appear together in two groups. This makes it easier to count. The first group contains 1 's', and the second group contains 4 's's. Additionally, there is 1 more 's' separate from these groups. By combining the counts from these groups and the additional 's', I arrive at a preliminary total of 6 's's. However, upon reviewing the options, I realize that I must consider the possibility of an error in my initial assessment.
    **Thinking time: 1.13 seconds**
    
    Step 2: Re-examining the Count of 's's in the Word 'mississssippi':
    I will recount the 's's in the word 'mississssippi'. Upon re-examination, I notice the groups of 's's are actually 'm-i-s-s-i-s-sss-ss-i-pp-i'. Recounting the groups, I still find two 's's separate from the groups and 4 in the last group. I still find 1 's' in a separate group at the start. Combining them I get 7 's's in the word. This seems correct, however, I must explore any possible alternative count. In considering my count, I consider the alternative the individual 's's in 'mississssippi' are not as grouped, but separate. I manually recount: the first 's', then 4 's's, plus 2 's's at the end of the groups gives me 7. Upon consideration, this approach still indicates there are 7 's's.
    **Thinking time: 1.21 seconds**
    
    Step 3: Validating the Count of 's's in the Word 'mississssippi':
    Considering the count I arrived at in the previous steps, I notice that I must further ensure the count is correct. There are no other apparent alternative methods to consider. Upon reflection on my approach, my confidence in my methods is high enough to proceed. However, this confidence does not exclude the possibility of an error.
    **Thinking time: 0.74 seconds**
    
    Final Answer:
    There are 7 's's in the word 'mississssippi'.
    **Thinking time: 0.42 seconds**
    
    **Total thinking time: 3.50 seconds**


As demonstrated in the COT Reasoning example, we can guide the model to break down the task into multiple steps and generate a coherent output. This allows the model to solve complex tasks in logical steps.
However, this requires multiple calls to the model, which may be expensive in terms of cost and time.
Also model may not always identify the correct steps to solve the task, hence is not deterministic.

# Conclusion
Chain of Thought Reasoning is a powerful technique that allows LLMs to solve complex tasks in logical steps. However, it requires multiple calls to the model and may not always identify the correct steps to solve the task. This technique can be useful when the task requires multi-step reasoning or logical thinking.

Care should be taken to ensure that the model is guided correctly and that the output is coherent and accurate.
