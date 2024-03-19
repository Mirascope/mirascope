# Dumping prompts and calls

The `.dump()` function can be called from prompts, calls, and responses to output a dictionary of associated data. 

## Dumping from the Prompt

When called from `BasePrompt` or any of its subclasses like `BaseCall`, `.dump()` will give you:

- the prompt template
- inputs used to construct the prompt
- the prompt’s tags
- any parameters specific to the model provider’s API call, if they are not None:
- start and end times of its affiliated completion, if it has happened

```python
import os

from mirascope import tags
from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


@tags(["recommendation_project", "version:0001"])
class BookRecommender(OpenAICall):
    prompt_template = "Can you recommend some books on {topic}?"

    topic: str


recommender = BookRecommender(topic="how to bake a cake")
print(recommender.dump())

"""
Output:
{
    "template": "Can you recommend some books on {topic}?",
    "inputs": {"api_key": None, "topic": "how to bake a cake"},
    "tags": ["recommendation_project", "version:0001"],
    "call_params": {"model": "gpt-3.5-turbo-0125"},
    "start_time_ms": None,
    "end_time_ms": None,
}
"""

recommender.call()
print(recommender.dump())

"""
Output:
{
	# ... same as above
    "start_time_ms": 1709847166609.473,
    "end_time_ms": 1709847169424.146,
}
"""
```

## Dumping from the Response

You can also call `.dump()` on responses themselves, which will contain:

- start and end times of the response
- parameters of the call to the API associated with the response, within the key “output”

```python
response = recomender.call()  # call is an OpenAICall, continued from above
print(response.dump())

"""
Output:
{
    "output": {
        "id": "chatcmpl-8zuVFGO2zgRsyckc9iW8CTSOgiNQm",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "logprobs": None,
                "message": {
                    "content": '1. "The Cake Bible" by Rose Levy Beranbaum...
					"role": "assistant",
                    "function_call": None,
                    "tool_calls": None,
                },
            }
        ],
        "created": 1709765897,
        "model": "gpt-3.5-turbo-0125",
        "object": "chat.completion",
        "system_fingerprint": "fp_2b778c6b35",
        "usage": {"completion_tokens": 210, "prompt_tokens": 19, "total_tokens": 229},
    },
}
"""
```

## Combining Both

We also give you an option to see everything at once by calling `BasePrompt.dump() | response.dump()` , which will union the two dictionaries and display them in one. Note that the `.dump()` function outputs a dictionary, so feel free to use it flexibly to suit your needs.

```python
print(recommender.dump(response.dump()))

"""
Output:
{
    "template": "Can you recommend some books on {topic}?",
    "inputs": {"api_key": None, "topic": "how to bake a cake"},
    "tags": ["recommendation_project", "version:0001"],
    "call_params": {"model": "gpt-3.5-turbo-0125"},
    "start_time": 1709837824962.49,
    "end_time": 1709837825585.0588,
    "output": {
        "id": "chatcmpl-8zuVFGO2zgRsyckc9iW8CTSOgiNQm",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "logprobs": None,
                "message": {
                    "content": '1. "The Cake Bible" by Rose Levy Beranbaum...
                    "role": "assistant",
                    "function_call": None,
                    "tool_calls": None,
                },
            }
        ],
        "created": 1709765897,
        "model": "gpt-3.5-turbo-0125",
        "object": "chat.completion",
        "system_fingerprint": "fp_2b778c6b35",
        "usage": {"completion_tokens": 210, "prompt_tokens": 19, "total_tokens": 229},
    },
}
"""
```

## Logging

Now that you have the JSON dump, it can be useful to log your responses:

```python
"""A basic example on how to log the data from a prompt and a chat completion."""
import logging
import os
from typing import Any, Optional

import pandas as pd
from sqlalchemy import JSON, Float, Integer, MetaData, String, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from mirascope import tags
from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

logger = logging.getLogger("mirascope")
TABLE_NAME = "openai_call_responses"


class Base(DeclarativeBase):
    pass


class OpenAICallResponseTable(Base):
    __tablename__ = TABLE_NAME
    id: Mapped[int] = mapped_column(
        Integer(), primary_key=True, autoincrement=True, nullable=False
    )
    template: Mapped[str] = mapped_column(String(), nullable=False)
    inputs: Mapped[Optional[dict]] = mapped_column(JSONB)
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON)
    call_params: Mapped[Optional[dict]] = mapped_column(JSONB)
    start_time: Mapped[Optional[float]] = mapped_column(Float(), nullable=False)
    end_time: Mapped[Optional[float]] = mapped_column(Float(), nullable=False)
    output: Mapped[Optional[dict]] = mapped_column(JSONB)


@tags(["recommendation_project"])
class BookRecommender(OpenAICall):
    prompt_template = "Can you recommend some books on {topic}?"

    topic: str


USERNAME = "root"
PASSWORD = ""
HOST = "localhost"
PORT = "5432"
DB_NAME = "mirascope"
engine = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}")


def create_database():
    """Create the database and table for the OpenAI call response."""
    metadata = MetaData()
    table_objects = [Base.metadata.tables[TABLE_NAME]]
    metadata.create_all(engine, tables=table_objects)


def log_to_database(recommender_response: dict[str, Any]):
    """Create a call response and log it to the database."""
    create_database()
    Session = sessionmaker(engine)
    with Session() as session:
        openai_completion_db = OpenAICallResponseTable(**recommender_response)
        session.add(openai_call_responses)
        session.commit()


def log_to_csv(recommender_response: dict[str, Any]):
    """Log the call response to a CSV file."""
    df = pd.DataFrame([recommender_response])
    with open("log.csv", "w") as f:
        df.to_csv(f, index=False)


def log_to_logger(recommender_response: dict[str, Any]):
    """Log the call response to the logger."""
    logger.info(recommender_response)


if __name__ == "__main__":
    recommender = BookRecommender(topic="how to bake a cake")
    response = recommender.call()
    recommender_response = recommender.dump() | response.dump()
    log_to_database(recommender_response)
    log_to_csv(recommender_response)
    log_to_logger(recommender_response)
```
