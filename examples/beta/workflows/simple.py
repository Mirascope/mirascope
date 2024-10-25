from __future__ import annotations

from random import randint

from mirascope.beta.workflows import step, NextStep, Workflow


@step()
def say_joke(topic: str) -> NextStep[rating]:
    return NextStep(rating, joke=f'joke for {topic=}')

@step()
def rating(joke: str) -> int:
    print(f'joke: {joke}')
    return randint(1, 10)

wf = Workflow(start=say_joke, stop=rating)
ret = wf.run(topic='cats')
print(ret.output)
