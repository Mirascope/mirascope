# Least to Most: Enhancing LLM Reasoning with Subproblem Decomposition

This recipe demonstrates how to implement the Least to Most technique using Large Language Models (LLMs) with Mirascope. Least to Most is a prompt engineering method that enhances an LLM's reasoning capabilities by breaking down complex problems into smaller, more manageable subproblems.

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
<a href="https://arxiv.org/pdf/2205.10625">Least to Most</a> is a more extensive version of <a href="https://arxiv.org/abs/2201.11903">Chain of Thought</a>, where separate calls are used to break down the original problem into subproblems as well as solve each individual step/subproblem. After solving each subproblem, the result is appended to the chat's history until the original problem is solved. Least to Most is an effective technique for symbolic and arithmetic reasoning tasks.
</p>
</div>

## Implementing Least to Most

Let's implement the Least to Most technique using Mirascope:



```python
from mirascope.core import openai, prompt_template
from mirascope.core.openai import OpenAICallResponse
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field

few_shot_examples = [
    {
        "question": "The median age in the city was 22.1 years. 10.1% of residents were under the age of 18; 56.2% were between the ages of 18 and 24; 16.1% were from 25 to 44; 10.5% were from 45 to 64; and 7% were 65 years of age or older. Which age group is larger: under the age of 18 or 18 and 24?",
        "answer": 'To answer the question "Which age group is larger: under the age of 18 or 18 and 24?", we need to know: "How many percent were under the age of 18?", "How many percent were between the ages of 18 and 24?".',
    },
    {
        "question": "Old age pensions were raised by 300 francs per month to 1,700 francs for a single person and to 3,700 francs for a couple, while health insurance benefits were made more widely available to unemployed persons and part-time employees. How many francs were the old age pensions for a single person before they were raised?",
        "answer": 'To answer the question "How many francs were the old age pensions for a single person before they were raised?", we need to know: "How many francs were the old age pensions for a single person?", "How many francs were old age pensions raised for a single person?".',
    },
    {
        "question": "In April 2011, the ECB raised interest rates for the first time since 2008 from 1% to 1.25%, with a further increase to 1.50% in July 2011. However, in 2012-2013 the ECB lowered interest rates to encourage economic growth, reaching the historically low 0.25% in November 2013. Soon after the rates were cut to 0.15%, then on 4 September 2014 the central bank reduced the rates from 0.15% to 0.05%, the lowest rates on record. How many percentage points did interest rates drop between April 2011 and September 2014?",
        "answer": 'To answer the question "How many percentage points did interest rates drop between April 2011 and September 2014?", we need to know: "What was the interest rate in April 2011?", "What was the interest rate in September 2014?".',
    },
    {
        "question": "Non-nationals make up more than half of the population of Bahrain. According to government statistics dated between 2005-2009 roughly 290,000 Indians, 125,000 Bangladeshis, 45,000 Pakistanis, 45,000 Filipinos, and 8,000 Indonesians. How many Pakistanis and Indonesians are in Bahrain?",
        "answer": 'To answer the question "How many Pakistanis and Indonesians are in Bahrain?", we need to know: "How many Pakistanis are in Bahrain?", "How many Indonesians are in Bahrain?".',
    },
]


class Problem(BaseModel):
    subproblems: list[str] = Field(
        ..., description="The subproblems that the original problem breaks down into"
    )


@openai.call(model="gpt-4o-mini", response_model=Problem)
@prompt_template(
    """
    Examples to guide your answer:
    {examples:lists}
    Break the following query into subproblems:
    {query}
    """
)
def break_into_subproblems(
    query: str, few_shot_examples: list[dict[str, str]]
) -> openai.OpenAIDynamicConfig:
    examples = [
        [f"Q:{example['question']}", f"A:{example['answer']}"]
        for example in few_shot_examples
    ]
    return {"computed_fields": {"examples": examples}}


@openai.call(model="gpt-4o-mini")
def call(history: list[ChatCompletionMessageParam]) -> str:
    return f"MESSAGES: {history}"


def least_to_most(query_context: str, query_question: str) -> OpenAICallResponse:
    problem = break_into_subproblems(
        query=query_context + query_question, few_shot_examples=few_shot_examples
    )
    history: list[ChatCompletionMessageParam] = [
        {"role": "user", "content": query_context + problem.subproblems[0]}
    ]
    response = call(history=history)
    history.append(response.message_param)
    if len(problem.subproblems) == 1:
        return response
    else:
        for i in range(1, len(problem.subproblems)):
            history.append({"role": "user", "content": problem.subproblems[i]})
            response = call(history=history)
            history.append(response.message_param)
        return response


query_context = """The Census Bureaus 2006-2010 American Community Survey showed that \
(in 2010 inflation adjustment dollars) median household income was $52,056 and the \
median family income was $58,942."""

query_question = "How many years did the Census Bureaus American Community Survey last?"

print(least_to_most(query_context=query_context, query_question=query_question))
```

    To calculate the duration between two years, you subtract the earlier year from the later year. The formula is:
    
    \[ \text{Duration} = \text{Later Year} - \text{Earlier Year} \]
    
    For example, if you want to calculate the duration between 2005 and 2010:
    
    \[ \text{Duration} = 2010 - 2005 = 5 \]
    
    So, the duration between 2005 and 2010 is 5 years.


This implementation consists of three main components:

1. `break_into_subproblems`: This function takes a query and breaks it down into subproblems using few-shot examples.
2. `call`: A simple function that makes a call to the LLM with the given message history.
3. `least_to_most`: This function orchestrates the Least to Most technique. It first breaks the problem into subproblems, then solves each subproblem sequentially, appending the results to the message history.

## Benefits and Considerations

The Least to Most implementation offers several advantages:

1. Improved reasoning for complex problems by breaking them down into manageable steps.
2. Enhanced ability to handle multi-step arithmetic and symbolic reasoning tasks.
3. Potential for more accurate responses by solving subproblems individually.

When implementing this technique, consider:

- Carefully crafting few-shot examples to guide the problem decomposition process.
- Balancing the number of subproblems to avoid oversimplification or overcomplexity.
- Ensuring that the query context and question are clear and contain all necessary information.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Complex Mathematical Problem Solving</b>: Use Least to Most for multi-step mathematical proofs or calculations.</li>
<li><b>Project Planning</b>: Break down large projects into smaller, manageable tasks.</li>
<li><b>Algorithmic Design</b>: Decompose complex algorithms into simpler steps for implementation.</li>
<li><b>Legal Case Analysis</b>: Break down complex legal cases into individual points of law to be addressed.</li>
<li><b>Medical Diagnosis</b>: Analyze symptoms and test results step-by-step to reach a diagnosis.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Tailoring the few-shot examples to your domain for better problem decomposition.
- Implementing a mechanism to handle interdependent subproblems.
- Combining Least to Most with other techniques like Self-Consistency for even more robust reasoning.
- Developing a feedback loop to refine the problem decomposition process based on the accuracy of final answers.

By leveraging Mirascope's `call` decorator, response models, and dynamic configuration, you can easily implement and customize the Least to Most technique to enhance your LLM's ability to reason about complex problems across a wide range of applications.
