"""How to log traces to LangSmith using Mirascope.

https://docs.smith.langchain.com/tracing/faq/logging_and_viewing#getting-the-url-of-a-logged-run
"""
import os
from uuid import uuid4

from langsmith import traceable, wrappers
from langsmith.run_trees import RunTree
from langsmith_config import Settings

from mirascope import BasePrompt, OpenAICallParams, OpenAIChat

settings = Settings()

os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class BookRecommendationPrompt(BasePrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str

    call_params = OpenAICallParams(model="gpt-3.5-turbo")


prompt = BookRecommendationPrompt(topic="how to bake a cake")

# Collect run ID using RunTree
run_id = uuid4()
rt = RunTree(
    name="OpenAI Call RunTree",
    run_type="llm",
    inputs={"messages": prompt.messages},
    id=run_id,
)
chat = OpenAIChat(client_wrapper=wrappers.wrap_openai)
completion = chat.create(prompt)
rt.end(outputs=completion.dump()["output"])
rt.post()
print("RunTree Run ID: ", run_id)

# Collect run ID using openai_wrapper
run_id = uuid4()
chat.create(prompt, langsmith_extra={"run_id": run_id})
print("OpenAI Wrapper Run ID: ", run_id)

# Collect run id using traceable decorator
run_id = uuid4()


@traceable(
    run_type="llm",
    name="OpenAI Call Decorator",
)
def call_openai() -> str:
    return str(chat.create(prompt))


result = call_openai(
    langsmith_extra={
        "run_id": run_id,
    },
)
print("Traceable Run ID: ", run_id)
