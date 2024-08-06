import inspect

from typing_extensions import TypedDict

from mirascope.core import openai, prompt_template


class FewShotExample(TypedDict):
    question: str
    answer: str


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Examples:
    {examples:lists}

    Query: {query}
    """
)
def self_ask(query: str, examples: list[FewShotExample]) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "examples": [
                [example["question"], example["answer"]] for example in examples
            ]
        }
    }


few_shot_examples = [
    FewShotExample(
        question="When does monsoon season end in the state the area code 575 is located?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Which state is the area code 575 located in?
            Intermediate answer: The area code 575 is located in New Mexico.
            Follow up: When does monsoon season end in New Mexico?
            Intermediate answer: Monsoon season in New Mexico typically ends in mid-September.
            So the final answer is: mid-September.
            """
        ),
    ),
    FewShotExample(
        question="What is the current official currency in the country where Ineabelle Diaz is a citizen?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Which country is Ineabelle Diaz a citizen of?
            Intermediate answer: Ineabelle Diaz is from Peurto Rico, which is in the United States of America.
            Follow up: What is the current official currency in the United States of America?
            Intermediate answer: The current official currency in the United States is the United States dollar.
            So the final answer is: United States dollar.
            """
        ),
    ),
    FewShotExample(
        question="Where was the person who founded the American Institute of Public Opinion in 1935 born?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Who founded the American Institute of Public Opinion in 1935?
            Intermediate answer: George Gallup.
            Follow up: Where was George Gallup born?
            Intermediate answer: George Gallup was born in Jefferson, Iowa.
            So the final answer is: Jefferson.
            """
        ),
    ),
    FewShotExample(
        question="What language is used by the director of Tiffany Memorandum?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Who directed the movie called Tiffany Memorandum?
            Intermediate answer: Sergio Grieco.
            Follow up: What language is used by Sergio Grieco?
            Intermediate answer: Sergio Grieco speaks Italian.
            So the final answer is: Italian.
            """
        ),
    ),
    FewShotExample(
        question="What is the sports team the person played for who scored the first touchdown in Superbowl 1?",
        answer=inspect.cleandoc(
            """
            Are follow up questions needed here: Yes.
            Follow up: Which player scored the first touchdown in Superbowl 1?
            Intermediate answer: Max McGee.
            Follow up: Which sports team did Max McGee play for?
            Intermediate answer: Max McGee played for the Green Bay Packers.
            So the final answer is: Green Bay Packers.
            """
        ),
    ),
]

query = "The birth country of Jayantha Ketagoda left the British Empire when?"
response = self_ask(query=query, examples=few_shot_examples)
print(response.content)
# > Are follow up questions needed here: Yes.
#   Follow up: What is the birth country of Jayantha Ketagoda?
#   Intermediate answer: Jayantha Ketagoda is from Sri Lanka.
#   Follow up: When did Sri Lanka leave the British Empire?
#   Intermediate answer: Sri Lanka, formerly known as Ceylon, gained independence from the British Empire on February 4, 1948.
#   So the final answer is: February 4, 1948.

response = self_ask(query=query, examples=[])
print(response.content)
# > Jayantha Ketagoda was born in Sri Lanka, which was known as Ceylon during the
#   British colonial period. Ceylon gained independence from the British Empire on
#   February 4, 1948.
