# Retries

Calls to LLM providers can fail due to various reasons, such as network issues, API rate limits, or service outages. To provide a resilient user experience and handle unexpected failures gracefully, Mirascope directly integrates with [Tenacity](https://tenacity.readthedocs.io/en/latest/).

## Call Retries

By passing the `retries` parameter to any Mirascope class that extends `BaseCall`, you can easily enable automatic retry functionality out of the box.  This will work for all of the `call`, `call_async`, `stream`, and `stream_async` methods. Using the same basic `RecipeRecommender` we can take advantage of tenacity to retry as many times as we need to generate a response that does not have certain words.

```python
import os

from mirascope import OpenAICall, OpenAICallParams
from tenacity import Retrying, retry_if_result

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

retries = Retrying(
    before=lambda details: print(details),
    after=lambda details: print(details),
    retry=retry_if_result(lambda result: "cheese" in result.content.lower()),
)

class RecipeRecommender(OpenAICall):
    prompt_template = "Recommend recipes that use {ingredient} as an ingredient"
    
    ingredient: str
    
    call_params = OpenAICallParams(model="gpt-3.5-turbo-0125")


response = RecipeRecommender(ingredient="apples").call(retries=retries)
print(response.content)  # Content will not contain "Cheese"
```

A more realistic usage of retries would involve making sure extraction works properly.

## Extraction Retries

Retries are also supported for any class that extends `BaseExtractor`. This is particularly useful for [extracting structured information](./extracting_structured_information_using_llms.md) because sometimes the model will fail to properly extract the schema. For example, if the model extracts a field with an incorrect type, this will result in a [`ValidationError`](https://docs.pydantic.dev/latest/errors/validation_errors/).

Often the failure can be a result of the prompt; however, sometimes it's simply a failure of the model. In such a case, the best course of action is to try the call again with the error message inserted into the prompt of the retried call. This helps the model identify and correct it's previous error. When using retries for extraction, Mirascope will automatically insert any errors into the next attempt.

If you want to retry the extraction up to some number of times, you can set `retries` equal to the number of runs (defaults to 0). Alternatively, you can pass in [tenacity.Retrying](https://tenacity.readthedocs.io/en/latest/) so that you can customize the behavior of retries. Mirascope will automatically pass in the error to the next call to give context. This will work for all of the `extract`, `extract_async`, `stream`, and `stream_async` methods.

We can take advantage of tenacity `retry_if_exception_type` to check for `ValidationError` and retry as necessary like so:

```python
from typing import Literal, Type

from pydantic import BaseModel, ValidationError
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt

from mirascope.openai import OpenAIExtractor


class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


class TaskExtractor(OpenAIExtractor[TaskDetails]):
    extract_schema: Type[TaskDetails] = TaskDetails
    prompt_template = """
    Extract the task details from the following task:
    {task}
    """

    task: str


retries = Retrying(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(ValidationError),
)
task = "Submit quarterly report by next Friday. Task is high priority."

task_details = TaskExtractor(task=task).extract(retries=retries)
```

If the extraction has a high failure rate even with retries, it can be a strong signal that the `prompt_template` needs to be improved.

As you can see, Mirascope makes extraction extremely simple. Under the hood, Mirascope uses the provided schema to extract the generated content and validate it (see [Validation](./extracting_structured_information_using_llms.md#validation) for more details).

```python
book = BookExtractor().extract(retries=3)  # will retry up to 3 times 
```
