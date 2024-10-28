from __future__ import annotations

import uuid
from pprint import pprint
from typing import Generator

from mirascope.beta.workflows import NextStep, Workflow, step, Join, JoinStep
from mirascope.core import openai


@openai.call("gpt-4o-mini")
def generate_joke(topic: str) -> str:
    return f"Write a joke about {topic}"


@openai.call("gpt-4o-mini")
def critique_joke(joke: str) -> str:
    return f"Critique this joke: {joke}"


@step()
def generate_multiple_joke(
    topic: str, count: int
) -> Generator[NextStep[generate_joke_step], None, None]:
    print(f"Generating {count} jokes about {topic}")
    group_id = str(uuid.uuid4())  # Generate a unique group ID
    for i in range(count):
        yield NextStep(
            generate_joke_step, topic=topic, group_id=group_id, expected_count=count
        )
    # After yielding all joke steps, yield a JoinStep to final_step


@step()
def generate_joke_step(
    topic: str, group_id: str, expected_count: int
) -> NextStep[critique_joke_step]:
    joke = generate_joke(topic).content
    print(f"Generated joke: {joke}")
    # Pass the group_id to maintain grouping
    return NextStep(
        critique_joke_step, joke=joke, group_id=group_id, expected_count=expected_count
    )


@step()
def critique_joke_step(
    joke: str, group_id: str, expected_count: int
) -> JoinStep[final_step]:
    critique = critique_joke(joke).content
    print(f"Generated critique: {critique}")
    # Return the critique directly
    return JoinStep(
        final_step, result=critique, group_id=group_id, expected_count=expected_count
    )


@step()
def final_step(multiple_input: Join[str]) -> str:
    print(f"Final step received results: {multiple_input.results}")
    critiques = [r.value for r in  multiple_input.results]
    return "\n\n".join(
        f"Critique {i+1}:\n{critique}" for i, critique in enumerate(critiques)
    )


workflow = Workflow(start=generate_multiple_joke, stop=final_step)
result = workflow.run("computer_science", 3)
pprint(result.output)
