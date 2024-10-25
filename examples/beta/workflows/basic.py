from __future__ import annotations

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


wf = Workflow(start=generate_joke_step, stop=critique_joke_step)
result = wf.run("computer_science")
print(result.output)
