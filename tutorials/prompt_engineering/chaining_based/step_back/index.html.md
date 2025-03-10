# Step-back Prompting: Enhancing LLM Reasoning with High-Level Questions

This recipe demonstrates how to implement the Step-back prompting technique using Large Language Models (LLMs) with Mirascope. Step-back prompting is a method that enhances an LLM's reasoning capabilities by asking a high-level question about relevant concepts or facts before addressing the original query.

<details class="tip">
<summary>Mirascope Concepts Used</summary>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
</ul>
</details>

<div class="admonition note">
<p class="admonition-title">Background</p>
<p><a href="https://arxiv.org/pdf/2310.06117">Step-back</a> prompting is an alternative to the Chain of Thought technique, where one asks the LLM a high-level question about relevant concepts or facts before asking it the actual question. This technique is derived from the fact that humans often take step backs and use abstractions to arrive at an answer, and it can yield correct answers at times when Chain of Thought fails.</p>
</div>

## Implementation

Let's implement the Step-back prompting technique using Mirascope:





```python
from mirascope.core import openai
from mirascope.core.base.prompt import prompt_template

few_shot_examples = [
    {
        "original_question": "Which position did Knox Cunningham hold from May 1955 to Apr 1956?",
        "stepback_question": "Which positions have Knox Cunningham held in his career?",
    },
    {
        "original_question": "Who was the spouse of Anna Karina from 1968 to 1974?",
        "stepback_question": "Who were the spouses of Anna Karina?",
    },
    {
        "original_question": "Which team did Thierry Audel play for from 2007 to 2008?",
        "stepback_question": "Which teams did Thierry Audel play for in his career?",
    },
    {
        "original_question": "What was the operator of GCR Class 11E from 1913 to Dec 1922?",
        "stepback_question": "What were the operators of GCR Class 11E in history?",
    },
    {
        "original_question": "Which country did Sokolovsko belong to from 1392 to 1525?",
        "stepback_question": "Which countries did Sokolovsko belong to in history?",
    },
    {
        "original_question": "when was the last time a team from canada won the stanley cup as of 2002",
        "stepback_question": "which years did a team from canada won the stanley cup as of 2002",
    },
    {
        "original_question": "when did england last get to the semi final in a world cup as of 2019",
        "stepback_question": "which years did england get to the semi final in a world cup as of 2019?",
    },
    {
        "original_question": "what is the biggest hotel in las vegas nv as of November 28, 1993",
        "stepback_question": "what is the size of the hotels in las vegas nv as of November 28, 1993",
    },
    {
        "original_question": "who has scored most runs in t20 matches as of 2017",
        "stepback_question": "What are the runs of players in t20 matches as of 2017",
    },
]

stepback_prompt = """You are an expert at world knowledge. Your task is to step \
back and paraphrase a question to a more generic step-back question, which is \
easier to answer. Here are a few examples:"""


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    SYSTEM: {stepback_prompt_and_examples}
    USER: {query}
    """
)
def get_stepback_question(
    query: str, num_examples: int = 0
) -> openai.OpenAIDynamicConfig:
    """Gets the generic, step-back version of a query."""
    if num_examples < 0 or num_examples > len(few_shot_examples):
        raise ValueError(
            "num_examples cannot be negative or greater than number of available examples."
        )
    example_prompts = ""
    for i in range(num_examples):
        example_prompts += (
            f"Original Question: {few_shot_examples[i]['original_question']}\n"
        )
        example_prompts += (
            f"Stepback Question: {few_shot_examples[i]['stepback_question']}\n"
        )
    return {
        "computed_fields": {
            "stepback_prompt_and_examples": f"{stepback_prompt}\n{example_prompts}"
            if num_examples
            else None
        }
    }


@openai.call(model="gpt-4o-mini")
def call(query: str) -> str:
    """A standard call to OpenAI."""
    return query


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    You are an expert of world knowledge. I am going to ask you a question.
    Your response should be comprehensive and not contradicted with the
    following context if they are relevant. Otherwise, ignore them if they are
    not relevant.

    {stepback_response}

    Original Question: {query}
    Answer:
    """
)
def stepback(query: str, num_examples: int) -> openai.OpenAIDynamicConfig:
    """Executes the flow of the Step-Back technique."""
    stepback_question = get_stepback_question(
        query=query, num_examples=num_examples
    ).content
    stepback_response = call(query=stepback_question).content
    return {"computed_fields": {"stepback_response": stepback_response}}


# Example usage
query = """Who is the highest paid player in the nba this season as of 2017"""

print(stepback(query=query, num_examples=len(few_shot_examples)))
```

    As of the 2017 NBA season, the highest-paid player was Stephen Curry. He signed a four-year, $215 million contract extension with the Golden State Warriors, which was the largest contract in NBA history at that time. This contract significantly boosted his earnings, making him the top earner in the league for that season. Other players like LeBron James and Kevin Durant were also among the highest-paid, but Curry's contract set a new benchmark in player salaries at that time.


This implementation consists of three main functions:

1. `get_stepback_question`: This function takes a query and generates a more generic, step-back version of the question.
2. `call`: A standard call to OpenAI that processes the step-back question.
3. `stepback`: This function orchestrates the Step-back prompting technique. It first calls `get_stepback_question` to generate a high-level question, then uses `call` to get a response to this question, and finally combines this information to answer the original query.

## Benefits and Considerations

The Step-back prompting implementation offers several advantages:

1. Improved reasoning about complex queries by considering higher-level concepts first.
2. Potential for more accurate responses in tasks that benefit from broader context.
3. Ability to overcome limitations of other techniques like Chain of Thought in certain scenarios.

When implementing this technique, consider:

- Balancing the generality of the step-back question with its relevance to the original query.
- Experimenting with different numbers of few-shot examples to optimize performance.
- Adjusting the prompt for generating step-back questions based on your specific use case.

<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Complex Problem Solving</b>: Use Step-back prompting for multi-step problems in fields like mathematics or engineering.</li>
<li><b>Medical Diagnosis</b>: Apply the technique to consider general symptoms before focusing on specific conditions.</li>
<li><b>Legal Analysis</b>: Implement Step-back prompting to first consider broader legal principles before addressing specific cases.</li>
<li><b>Historical Analysis</b>: Use the method to first consider broader historical context before analyzing specific events.</li>
<li><b>Product Development</b>: Apply Step-back prompting to consider general market trends before focusing on specific product features.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider:

- Tailoring the few-shot examples to your domain for better performance.
- Implementing a feedback loop to continuously improve the quality of step-back questions generated.
- Combining Step-back prompting with other techniques like Self-consistency for even more robust reasoning capabilities.
- Experimenting with different LLM models to find the best balance between performance and efficiency for your use case.

By leveraging Mirascope's `call` decorator and dynamic configuration, you can easily implement and customize the Step-back prompting technique to enhance your LLM's reasoning capabilities across a wide range of applications.
