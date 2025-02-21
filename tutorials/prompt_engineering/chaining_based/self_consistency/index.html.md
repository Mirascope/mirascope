# Self-Consistency: Enhancing LLM Reasoning with Multiple Outputs

This recipe demonstrates how to implement the Self-Consistency technique using Large Language Models (LLMs) with Mirascope. Self-Consistency is a prompt engineering method that enhances an LLM's reasoning capabilities by generating multiple Chain of Thought (CoT) responses and selecting the most common answer. We'll explore both a basic implementation and an enhanced version with automated answer extraction.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
<li><a href="../../../../learn/response_models/">Response Models</a></li>
</ul>
</div>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
Self-consistency is a prompt engineering technique where multiple calls are made with Chain of Thought prompting, resulting in various answers, and the most common answer is selected. Self-consistency has shown to be highly effective on mathematical and symbolic reasoning, and has also been shown to help in niche scenarios where CoT actually reduces the quality of LLM output.
</p>
<p>
In the <a href="https://arxiv.org/pdf/2203.11171">original paper</a>, users manually pick the most frequent response, but we have integrated response models to automate that process once all responses have been generated.
</p>
</div>

## Basic Self-Consistency Implementation

Let's start with a basic implementation of Self-Consistency using Chain of Thought reasoning:



```python
import asyncio
from collections import Counter

from mirascope.core import openai, prompt_template

few_shot_examples = [
    {
        "question": "There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?",
        "answer": "We start with 15 trees. Later we have 21 trees. The difference must be the number of trees they planted. So, they must have planted 21 - 15 = 6 trees. The answer is 6.",
    },
    {
        "question": "If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?",
        "answer": "There are 3 cars in the parking lot already. 2 more arrive. Now there are 3 + 2 = 5 cars. The answer is 5.",
    },
    {
        "question": "Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?",
        "answer": "Leah had 32 chocolates and Leah’s sister had 42. That means there were originally 32 + 42 = 74 chocolates. 35 have been eaten. So in total they still have 74 - 35 = 39 chocolates. The answer is 39.",
    },
    {
        "question": "Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?",
        "answer": "Jason had 20 lollipops. Since he only has 12 now, he must have given the rest to Denny. The number of lollipops he has given to Denny must have been 20 - 12 = 8 lollipops. The answer is 8.",
    },
    {
        "question": "Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?",
        "answer": "He has 5 toys. He got 2 from mom, so after that he has 5 + 2 = 7 toys. Then he got 2 more from dad, so in total he has 7 + 2 = 9 toys. The answer is 9.",
    },
    {
        "question": "There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?",
        "answer": "There are 4 days from monday to thursday. 5 computers were added each day. That means in total 4 * 5 = 20 computers were added. There were 9 computers in the beginning, so now there are 9 + 20 = 29 computers. The answer is 29.",
    },
    {
        "question": "Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?",
        "answer": "Michael initially had 58 balls. He lost 23 on Tuesday, so after that he has 58 - 23 = 35 balls. On Wednesday he lost 2 more so now he has 35 - 2 = 33 balls. The answer is 33.",
    },
]


@openai.call(model="gpt-4o-mini", call_params={"temperature": 0.5})
@prompt_template(
    """
    Some examples on how to think step by step:
    {examples:lists}

    Answer the following question, thinking step by step:
    {query}
    """
)
async def chain_of_thought(
    query: str, few_shot_examples: list[dict[str, str]]
) -> openai.OpenAIDynamicConfig:
    examples = [
        [f"Q:{example['question']}", f"A:{example['answer']}"]
        for example in few_shot_examples
    ]
    return {"computed_fields": {"examples": examples}}


def most_frequent(lst):
    """Returns the most frequent element in a list."""
    counter = Counter(lst)
    most_common = counter.most_common(1)
    return most_common[0][0] if most_common else None


async def self_consistency(
    query: str, num_samples: int, few_shot_examples: list[dict[str, str]]
):
    cot_tasks = [chain_of_thought(query, few_shot_examples) for _ in range(num_samples)]
    cot_responses = [response.content for response in await asyncio.gather(*cot_tasks)]
    # Extract final answers manually (simplified for this example)
    final_answers = [
        response.split("The answer is ")[-1].strip(".") for response in cot_responses
    ]
    return most_frequent(final_answers)


query = "Olivia has $23. She bought five bagels for $3 each. How much money does she have left?"
result = await self_consistency(
    query=query, num_samples=5, few_shot_examples=few_shot_examples
)
print(f"The most consistent answer is: {result}")
```

    The most consistent answer is: $8


This basic implementation demonstrates how to use Self-Consistency with Chain of Thought reasoning. The `self_consistency` function generates multiple CoT responses and selects the most frequent final answer.

## Enhanced Self-Consistency with Automated Answer Extraction

Now, let's improve our implementation by adding automated answer extraction:


```python
from pydantic import BaseModel, Field


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


async def enhanced_self_consistency(
    query: str, num_samples: int, few_shot_examples: list[dict[str, str]]
) -> int:
    cot_tasks = [chain_of_thought(query, few_shot_examples) for _ in range(num_samples)]
    cot_responses = [response.content for response in await asyncio.gather(*cot_tasks)]
    extract_number_tasks = [extract_number(response) for response in cot_responses]
    response_numbers = [
        response.solution_value
        for response in await asyncio.gather(*extract_number_tasks)
    ]
    return most_frequent(response_numbers)


result = await enhanced_self_consistency(
    query=query, num_samples=5, few_shot_examples=few_shot_examples
)
print(f"The most consistent answer is: {result}")
```

    The most consistent answer is: 8



This enhanced version introduces the `extract_number` function, which uses a response model to automatically extract the numerical answer from each CoT response. The `enhanced_self_consistency` function then uses this extracted number to determine the most consistent answer.

## Benefits and Considerations

The Self-Consistency implementation offers several advantages:

1. Improved accuracy on mathematical and symbolic reasoning tasks.
2. Mitigation of occasional errors or inconsistencies in LLM outputs.
3. Potential for better performance in scenarios where standard CoT might struggle.

When implementing this technique, consider:

- Balancing the number of samples with computational cost and time constraints.
- Adjusting the temperature parameter to control the diversity of generated responses.
- Fine-tuning the answer extraction process for different types of problems (e.g., numerical vs. categorical answers).

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Complex Problem Solving</b>: Use Self-Consistency for multi-step problems in fields like physics or engineering.</li>
<li><b>Medical Diagnosis</b>: Apply Self-Consistency to improve the accuracy of symptom analysis and potential diagnoses.</li>
<li><b>Financial Modeling</b>: Implement Self-Consistency for more reliable financial predictions and risk assessments.</li>
<li><b>Natural Language Understanding</b>: Enhance text classification or sentiment analysis tasks with Self-Consistency.</li>
<li><b>Educational Assessment</b>: Use Self-Consistency to generate and validate multiple-choice questions and answers.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Tailoring the few-shot examples to your domain for better performance.
- Experimenting with different prompt formats and Chain of Thought structures.
- Implementing a feedback loop to continuously improve the quality of the Self-Consistency responses.
- Combining Self-Consistency with other techniques like Self-Ask for even more powerful reasoning capabilities.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the Self-Consistency technique to enhance your LLM's reasoning capabilities across a wide range of applications.

