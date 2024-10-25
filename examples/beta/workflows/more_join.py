from __future__ import annotations

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
def generate_other_topic_step(topic: str) -> NextStep[critique_joke_step]:
    joke = generate_other_topic(topic).content
    print(f"Generated joke: {joke}")
    return NextStep(critique_joke_step, joke=joke)


@step()
def generate_joke_step(topic: str) -> NextStep[critique_joke_step]:
    joke = generate_joke(topic).content
    print(f"Generated joke: {joke}")
    return NextStep(critique_joke_step, joke=joke)


@step()
def generate_multiple_joke(
    topic: str, count: int
) -> Generator[
    NextStep[generate_joke_step] | NextStep[generate_other_topic_step], None, None
]:
    print(f"Generating {count} jokes about {topic}")
    for i in range(count):
        yield NextStep(generate_joke_step, topic=topic)
    yield NextStep(generate_other_topic_step, topic=topic)


@step()
def critique_joke_step(joke: str) -> JoinStep[final_step]:
    critique = critique_joke(joke).content
    return JoinStep(final_step, result=critique)


@step()
def final_step(multiple_input: Join[critique_joke_step]) -> str:
    print(f"Final step received results: {multiple_input.results}")
    critiques = multiple_input.results
    return "\n\n".join(
        f"Critique {i+1}:\n{critique}" for i, critique in enumerate(critiques)
    )


workflow = Workflow(start=generate_multiple_joke, stop=final_step)
result = workflow.run("computer_science", 3)
pprint(len(result.output))
pprint(result.output)
