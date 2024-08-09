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

stepback_prompt = """You are an expert at world knowledge. Your task is to step
back and paraphrase a question to a more generic step-back question, which is
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
            else ""
        }
    }


@openai.call(model="gpt-4o-mini")
@prompt_template("""{query}""")
def call(query: str):
    """A standard call to OpenAI."""


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
    # Uncomment to see intermediate responses
    # print(stepback_question)
    # print(stepback_response)
    return {"computed_fields": {"stepback_response": stepback_response}}


query = """Who is the highest paid player in the nba this season as of 2017"""

print(stepback(query=query, num_examples=len(few_shot_examples)))
# > The highest-paid player in the NBA during the 2017 season was Stephen Curry of the Golden State Warriors, earning approximately $34.7 million.


# Intermediate Responses

# stepback_question = get_stepback_question(query=query, num_examples=num_examples)
# > Who were the highest paid players in the NBA during the 2017 season?

# stepback_response = call(stepback_question)
# > During the 2017 NBA season, the highest-paid players primarily included superstars with maximum contracts. Here are some of the top earners for that season:
#
#   1. **Stephen Curry** - Golden State Warriors: Approximately $34.7 million
#   2. **LeBron James** - Cleveland Cavaliers: Approximately $31.3 million
#   3. **Kevin Durant** - Golden State Warriors: Approximately $25.0 million
#   4. **James Harden** - Houston Rockets: Approximately $28.3 million
#   5. **Russell Westbrook** - Oklahoma City Thunder: Approximately $26.5 million
