# Dumping prompts

The `.dump()` function can be called from both prompts and completions to output a dictionary of associated data. 

## Dumping from the Prompt

When called from `BasePrompt` or any of its subclasses, `.dump()` will give you:

- the prompt template
- inputs used to construct the prompt
- the prompt’s tags
- any parameters specific to the model provider’s API call, if they are not None:
- start and end times of its affiliated completion, if it has happened

```python
import os

from mirascope import tags
from mirascope.openai import OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


@tags(["recommendation_project", "version:0001"])
class BookRecommendationPrompt(OpenAIPrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")
print(prompt.dump())

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

prompt.create()
print(prompt.dump())

"""
Output:
{
	# ... same as above
    "start_time_ms": 1709847166609.473,
    "end_time_ms": 1709847169424.146,
}
"""
```

## Dumping from the Completion

*(Support for Gemini and Mistral completions coming soon…)*

You can also call `.dump()` on chat completions themselves, which will contain:

- start and end times of the completion
- parameters of the call to the OpenAI API associated with the completion, within the key “output”

```python
completion = prompt.create() # prompt is an OpenAIPrompt, continued from above
print(completion.dump())

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

We also give you an option to see everything at once by calling `BasePrompt.dump(completion.dump())` , which will append the two dictionaries and display them in one. Note that the `.dump()` function will take any dictionary and append it to the data of the prompt, so feel free to use it flexibly to suit your needs.

```python
print(prompt.dump(completion.dump()))

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

Now that you have the JSON dump, it can be useful to log your completions:

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
from mirascope.openai import OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

logger = logging.getLogger("mirascope")
TABLE_NAME = "openai_chat_completions"


class Base(DeclarativeBase):
    pass


class OpenAIChatCompletionTable(Base):
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
class BookRecommendationPrompt(OpenAIPrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


USERNAME = "root"
PASSWORD = ""
HOST = "localhost"
PORT = "5432"
DB_NAME = "mirascope"
engine = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}")


def create_database():
    """Create the database and table for the OpenAI chat completions."""
    metadata = MetaData()
    table_objects = [Base.metadata.tables[TABLE_NAME]]
    metadata.create_all(engine, tables=table_objects)


def log_to_database(prompt_completion: dict[str, Any]):
    """Create a prompt completion and log it to the database."""
    create_database()
    Session = sessionmaker(engine)
    with Session() as session:
        openai_completion_db = OpenAIChatCompletionTable(**prompt_completion)
        session.add(openai_completion_db)
        session.commit()


def log_to_csv(prompt_completion: dict[str, Any]):
    """Log the prompt completion to a CSV file."""
    df = pd.DataFrame([prompt_completion])
    with open("log.csv", "w") as f:
        df.to_csv(f, index=False)


def log_to_logger(prompt_completion: dict[str, Any]):
    """Log the prompt completion to the logger."""
    logger.info(prompt_completion)


if __name__ == "__main__":
    prompt = BookRecommendationPrompt(topic="how to bake a cake")
    completion = prompt.create()
    prompt_completion = prompt.dump(completion.dump())
    log_to_database(prompt_completion)
    log_to_csv(prompt_completion)
    log_to_logger(prompt_completion)
```
