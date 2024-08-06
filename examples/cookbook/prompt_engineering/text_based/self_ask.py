import inspect

import numpy as np
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from mirascope.core import openai, prompt_template


class FewShotExample(BaseModel):
    question: str
    answer: str

    def messages(
        self,
    ) -> tuple[ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam]:
        """Returns a user -> assistant message pair as a chat turn example."""
        return (
            {"role": "user", "content": self.question},
            {"role": "assistant", "content": self.answer},
        )


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    MESSAGES: {example_prompts}
    USER: {query}
    """
)
def call(query: str, examples: list[FewShotExample]) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "example_prompts": [
                message for example in examples for message in example.messages()
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


response = call(
    query="The birth country of Jayantha Ketagoda left the British Empire when?",
    examples=few_shot_examples,
)
print(response.content)
# > Jayantha Ketagoda is from Sri Lanka. Sri Lanka, formerly known as Ceylon, gained
#   independence from the British Empire on February 4, 1948. So, the final answer is:
#   February 4, 1948.


def select_relevant_examples(
    query: str, examples: list[FewShotExample], n: int = 3
) -> list[FewShotExample]:
    """Select the most relevant examples based on cosine similarity."""
    vectorizer = TfidfVectorizer().fit([ex.question for ex in examples] + [query])
    example_vectors = vectorizer.transform([ex.question for ex in examples])
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(query_vector, example_vectors)[0]
    most_similar_indices = np.argsort(similarities)[-n:][::-1]

    return [examples[i] for i in most_similar_indices]


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    MESSAGES: {example_prompts}
    USER: {query}
    """
)
def dynamic_self_ask_query(
    query: str, examples: list[FewShotExample], n: int = 3
) -> openai.OpenAIDynamicConfig:
    relevant_examples = select_relevant_examples(query, examples, n)
    return {
        "computed_fields": {
            "example_prompts": [
                message
                for example in relevant_examples
                for message in example.messages()
            ]
        }
    }


query = "What was the primary language spoken by the inventor of the phonograph?"
response = dynamic_self_ask_query(query=query, examples=few_shot_examples, n=2)
print(response.content)
# > Are follow up questions needed here: Yes.
#   Follow up: Who invented the phonograph?
#   Intermediate answer: Thomas Edison.
#   Follow up: What language did Thomas Edison primarily speak?
#   Intermediate answer: Thomas Edison primarily spoke English.
#   So the final answer is: English.
