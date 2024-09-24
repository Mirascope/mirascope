import json
import os
import uuid
from collections.abc import Callable

from openai import OpenAI
from openai.types import Batch
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


class OpenAIBatch:
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

    job: Batch

    def __init__(self, filename: str = "./batch_job.jsonl", **kwargs: dict) -> None:
        self.filename = filename
        self.client = OpenAI(
            api_key=str(kwargs.get("OPENAI_API_KEY", os.environ["OPENAI_API_KEY"]))
        )

    def add(
        self,
        func: Callable[..., list[BaseMessageParam]],
        model: str,
        data: list[str],
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

        with open(self.filename, "a") as f:
            for task in tasks:
                f.write(json.dumps(task) + "\n")

    def run(self) -> None:
        with open(self.filename, "rb") as f:
            batch_file = self.client.files.create(file=f, purpose="batch")

        self.job = self.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )

    def is_in_progress(self) -> bool:
        self.job = self.client.batches.retrieve(self.job.id)
        return self.job.status not in ["failed", "completed"]

    def retrieve(self, result_file_name: str = "results.jsonl") -> list | None:
        self.job = self.client.batches.retrieve(self.job.id)

        if self.job.status == "completed":
            result_file_id = self.job.output_file_id
            if result_file_id:
                result = self.client.files.content(result_file_id).content

                with open(result_file_name, "wb") as file:
                    file.write(result)

                results = []
                with open(result_file_name) as file:
                    for line in file:
                        json_object = json.loads(line.strip())
                        results.append(json_object)
                return results
