from __future__ import annotations

from typing import Generator

from mirascope.beta.workflows import NextStep, Workflow, step
from mirascope.core import openai


@openai.call("gpt-4o-mini")
def generate_joke(topic: str) -> str:
    return f"Write a joke about {topic}"


@step()
def generate_joke_step(topic: str) -> NextStep[critique_joke_step]:
    joke = generate_joke(topic).content
    return NextStep(critique_joke_step, joke=joke)


@openai.call("gpt-4o-mini")
def critique_joke(joke: str) -> str:
    return f"Critique this joke: {joke}"


@step()
def critique_joke_step(joke: str) -> str:
    critique = critique_joke(joke)
    return critique.content


@step()
def generate_multiple_joke(
    topic: str, count: int
) -> Generator[NextStep[generate_joke_step], None, None]:
    for i in range(count):
        yield NextStep(generate_joke_step, topic=topic)


wf = Workflow(start=generate_multiple_joke, stop=critique_joke_step)
result = wf.run("computer_science", 3)
print(len(result.output))
print(result.output)
