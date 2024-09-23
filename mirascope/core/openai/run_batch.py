import os

import openai


def run_batch(batch_filename: str, **kwargs: dict) -> openai.types.Batch:
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
