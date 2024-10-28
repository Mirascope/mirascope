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


@openai.call("gpt-4o-mini")
def generate_other_topic(topic: str) -> str:
    return f"Generate other topic from {topic}"


@step()
def generate_multiple_joke(
    topic: str, count: int
) -> Generator[
    NextStep[generate_joke_step]
    | NextStep[generate_other_topic_step]
    | JoinStep[final_step],
    None,
    None,
]:
    print(f"Generating {count} jokes about {topic}")
    group_id = str(uuid.uuid4())
    expected_count = count + 1  # Number of jokes generated
    for i in range(count):
        yield NextStep(
            generate_joke_step,
            topic=topic,
            group_id=group_id,
            expected_count=expected_count,
        )
    yield NextStep(
        generate_other_topic_step,
        topic=topic,
        group_id=group_id,
        expected_count=expected_count,
    )


@step()
def generate_joke_step(
    topic: str, group_id: str, expected_count: int
) -> JoinStep[final_step]:
    joke = generate_joke(topic).content
    print(f"Generated joke: {joke}")
    # Return a JoinStep with group_id but without specifying expected_count here
    return JoinStep(
        final_step, result=joke, group_id=group_id, expected_count=expected_count
    )


@step()
def generate_other_topic_step(
    topic: str, group_id: str, expected_count: int
) -> JoinStep[final_step]:
    joke = generate_other_topic(topic).content
    print(f"Generated joke: {joke}")
    return JoinStep(
        final_step, result=joke, group_id=group_id, expected_count=expected_count
    )


@step()
def final_step(multiple_input: Join[str]) -> str:
    print(f"Final step received results len: {len(multiple_input.results)}")
    return "\n\n".join(f"Joke {i+1}. {r.step_full_qualname}:\n{r.value}" for i, r in enumerate(multiple_input.results))


workflow = Workflow(start=generate_multiple_joke, stop=final_step)
result = workflow.run("computer_science", 3)
pprint(result.output)
