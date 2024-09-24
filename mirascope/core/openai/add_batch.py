"""This module contains the `add_batch` function."""

import json
import uuid
from collections.abc import Callable

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from ..base import BaseMessageParam
from ._utils import convert_message_params


class RequestBody(BaseModel):
    model: str
    messages: list[ChatCompletionMessageParam]


class Request(BaseModel):
    custom_id: str
    method: str
    url: str
    body: RequestBody


def add_batch(
    func: Callable[..., list[BaseMessageParam]],
    model: str,
    data: list[str],
    batch_filename: str = "./batch_job.jsonl",
) -> None:
    tasks = []
    for d in data:
        request = Request(
            custom_id=f"task-{uuid.uuid4()}",
            method="POST",
            url="/v1/chat/completions",
            body=RequestBody(
                model=model,
                messages=convert_message_params(func(d)),  # noqa: F401 #type: ignore
            ),
        )

        tasks.append(request.model_dump())

    with open(batch_filename, "a") as f:
        for task in tasks:
            f.write(json.dumps(task) + "\n")


"""
Example:

```python
from mirascope.core import openai, prompt_template
import time

@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...

openai.add_batch(recommend_book, "gpt-4o-mini", data=["fantasy", "horror"])
batch = openai.run_batch()

while batch.status != "completed":
    print(f"waiting 5 seconds")
    time.sleep(5)
    print(openai.retrieve_batch(batch))
```
"""
