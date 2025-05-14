# Chain of Thought

[Chain of Thought](https://arxiv.org/pdf/2201.11903) (CoT) is a common prompt engineering technique which asks the LLM to step through its reasoning and thinking process to answer a question. In its simplest form, it can be implemented by asking asking the LLM to step through a problem step by step, but is more effective when you leverage examples and patterns of reasoning similar to your query in a few shot prompt. Chain of Thought is most effective for mathematical and reasoning tasks.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
</ul>
</div>

## Zero Shot CoT

<div class="admonition note">
<p class="admonition-title">Note</p>
<p>Recent models will automatically explain their reasoning (to a degree) for most reasoning tasks, but explicitly asking for a step by step solution can sometimes produce better solutions and explanations.</p>
</div>



```python
from mirascope.core import openai, prompt_template

cot_augment = "\nLet's think step by step."


@openai.call(model="gpt-4o-mini")
@prompt_template("{query} {cot_augment}")
def call(query: str, cot_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "cot_augment": cot_augment if cot_prompt else "",
        }
    }


prompt = """Olivia has $23. She bought five bagels for $3 each.
How much money does she have left?"""

print(call(query=prompt, cot_prompt=True))
```

    First, let's determine how much money Olivia spent on the bagels.
    
    1. **Calculate the total cost of the bagels:**
       - Price of one bagel = $3
       - Number of bagels = 5
       - Total cost = Price of one bagel × Number of bagels = $3 × 5 = $15
    
    2. **Subtract the total cost from Olivia's initial amount:**
       - Initial amount = $23
       - Amount spent = $15
       - Amount left = Initial amount - Amount spent = $23 - $15 = $8
    
    So, Olivia has $8 left after buying the bagels.


## Few Shot CoT


```python
from mirascope.core import openai
from openai.types.chat import ChatCompletionMessageParam

few_shot_examples = [
    {
        "question": "There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?",
        "answer": """There are 15 trees originally. Then there were 21 trees after some more were planted. So there must have been 21 - 15 = 6. The answer is 6.""",
    },
    {
        "question": "If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?",
        "answer": """There are originally 3 cars. 2 more cars arrive. 3 + 2 = 5. The answer is 5.""",
    },
    {
        "question": "Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?",
        "answer": """Originally, Leah had 32 chocolates. Her sister had 42. So in total they had 32 + 42 = 74. After eating 35, they had 74 - 35 = 39. The answer is 39.""",
    },
    {
        "question": "Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?",
        "answer": """Jason started with 20 lollipops. Then he had 12 after giving some to Denny. So he gave Denny 20 - 12 = 8. The answer is 8.""",
    },
    {
        "question": "Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?",
        "answer": """Shawn started with 5 toys. If he got 2 toys each from his mom and dad, then that is 4 more toys. 5 + 4 = 9. The answer is 9.""",
    },
    {
        "question": "There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?",
        "answer": """There were originally 9 computers. For each of 4 days, 5 more computers were added. So 5 * 4 = 20 computers were added. 9 + 20 is 29. The answer is 29.""",
    },
    {
        "question": "Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?",
        "answer": """Michael started with 58 golf balls. After losing 23 on tuesday, he had 58 - 23 = 35. After losing 2 more, he had 35 - 2 = 33 golf balls. The answer is 33.""",
    },
]


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    MESSAGES: {example_prompts}
    USER: {query}
    """
)
def call(query: str, num_examples: int = 0) -> openai.OpenAIDynamicConfig:
    if num_examples < 0 or num_examples > len(few_shot_examples):
        raise ValueError(
            "num_examples cannot be negative or greater than number of available examples."
        )
    example_prompts: list[ChatCompletionMessageParam] = []
    for i in range(num_examples):
        example_prompts.append(
            {"role": "user", "content": few_shot_examples[i]["question"]}
        )
        example_prompts.append(
            {"role": "assistant", "content": few_shot_examples[i]["answer"]}
        )
    return {"computed_fields": {"example_prompts": example_prompts}}


prompt = """Olivia has $23. She bought five bagels for $3 each.
How much money does she have left?"""

print(call(query=prompt, num_examples=len(few_shot_examples)))
```

    Olivia bought 5 bagels for $3 each, which costs her a total of \(5 \times 3 = 15\) dollars. 
    
    She started with $23, so after the purchase, she has \(23 - 15 = 8\) dollars left. 
    
    The answer is $8.


<div class="admonition tip">
<p class="admonition-title">Effective Chain of Thought Usage</p>
<ul>
<li><strong>Encourage Step-by-Step Thinking</strong>: Explicitly instruct the LLM to break down the problem into small steps.</li>
<li><strong>Provide Relevant Examples</strong>: In few-shot learning, use examples that are similar to the problem you want to solve.</li>
<li><strong>Ask for Clear Explanations</strong>: Prompt the LLM to explain its reasoning clearly at each step.</li>
<li><strong>Apply to Complex Problems</strong>: Chain of Thought is particularly effective for problems that require multiple steps or complex reasoning.</li>
<li><strong>Validate Results</strong>: Review the LLM's reasoning process and verify that each step is logical.</li>
</ul>
</div>

By leveraging the Chain of Thought technique, you can make the LLM's reasoning process more transparent and obtain more accurate and explainable answers to complex problems. This technique is particularly useful for mathematical problems and tasks that require multi-step reasoning.
