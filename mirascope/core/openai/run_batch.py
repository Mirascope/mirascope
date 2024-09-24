import os

import openai


def run_batch(
    batch_filename: str = "./batch_job.jsonl", **kwargs: dict
) -> openai.types.Batch:
    api_key = kwargs.get("OPENAI_API_KEY", os.environ["OPENAI_API_KEY"])
    client = openai.OpenAI(api_key=str(api_key))
    with open(batch_filename, "rb") as f:
        batch_file = client.files.create(file=f, purpose="batch")

    batch_job = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    return batch_job


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
