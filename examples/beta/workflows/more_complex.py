from __future__ import annotations

import inspect

from typing_extensions import NotRequired

from mirascope.beta.workflows import BaseContext, NextStep, step, Workflow
from mirascope.core import openai


class Context(BaseContext):
    topic: NotRequired[str]
    critique: NotRequired[str]


@openai.call("gpt-4o-mini")
def generate_joke(topic: str, critique: str | None = None) -> str:
    if critique:
        return f"Write a joke about {topic} taking into account: {critique}"
    return f"Write a joke about {topic}"


@step()
def generate_joke_step(topic: str, context: Context) -> NextStep[critique_joke_step]:
    joke = generate_joke(topic, context.get("critique")).content
    context["topic"] = topic
    return NextStep(critique_joke_step, joke=joke)


@openai.call("gpt-4o-mini")
def critique_joke(joke: str) -> str:
    return f"Critique this joke: {joke}"


@step()
def critique_joke_step(joke: str, context: Context) -> NextStep[regenerate_joke]:
    context["critique"] = critique_joke(joke).content
    return NextStep(regenerate_joke, joke)


@openai.call("gpt-4o-mini", response_model=float)
def rating_joke(joke: str, critique: str) -> float:
    return inspect.cleandoc(f"""
    Give a 1-5 rating for the following joke based on the critique:
    Joke: {joke}
    Critique: {critique}
    """)


@step()
def regenerate_joke(joke: str, context: Context) -> str | NextStep[generate_joke_step]:
    critique = context.get("critique")
    rating = rating_joke(joke, critique=critique)
    if rating < 4:
        return NextStep(generate_joke_step, topic=context["topic"])
    return joke


wf = Workflow(start=generate_joke_step, stop=regenerate_joke)
result = wf.run("computer science")

print(result.output)
