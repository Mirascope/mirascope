import json
import os

import openai
from openai.types import Batch


def retrieve_batch(
    batch_job: Batch, result_file_name: str = "results.jsonl", **kwargs: dict
) -> list | None:
    api_key = kwargs.get("OPENAI_API_KEY", os.environ["OPENAI_API_KEY"])
    client = openai.OpenAI(api_key=str(api_key))
    result_file_id = batch_job.output_file_id
    if result_file_id:
        result = client.files.content(result_file_id).content

        with open(result_file_name, "wb") as file:
            file.write(result)

        results = []
        with open(result_file_name) as file:
            for line in file:
                json_object = json.loads(line.strip())
                results.append(json_object)
        return results
