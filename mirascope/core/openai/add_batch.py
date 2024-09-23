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
            url="",
            body=RequestBody(
                model=model,
                messages=convert_message_params(func(d)),  # noqa: F401 #type: ignore
            ),
        )

        tasks.append(request.dict())

    with open(batch_filename, "a") as f:
        for task in tasks:
            f.write(json.dumps(task) + "\n")


"""


Example:

```python
import time

from mirascope.core import openai, prompt_template

@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


@openai.call("gpt-4")
@prompt_template("Recommend a meal from {cuisine} cuisine")
def recommend_food(cuisine: str): ...

dummy_data_genres = ["fantasy", "mystery", "scifi"]
dummy_data_cuisines = ["italian", "mexican", "french"]

batch_filename = "batch_job.jsonl"
openai.add_batch(recommend_book, dummy_data_genres, batch_filename )
openai.add_batch(recommend_food, dummy_data_cuisines, batch_filename) #file defaults to "./batch_job.jsonl" or whatever anyways

job = openai.run_batch(batch_filename, auto_fetch=True) # returns `OpenAIBatchJob` class or something that will automatically pull the responses from OpenAI when its done
while not job.complete:  # easy polling for completion, could also save the job and load it later or something with pydantic serialization
    time.sleep(100)
print(job.results)  # ideally this would be able to handle not just content or JSON mode but also things like `response_model` natively

# Along the way, there might be a file that is created like batch_job_links.jsonl that has a list completion request ids -> functions
```
"""
