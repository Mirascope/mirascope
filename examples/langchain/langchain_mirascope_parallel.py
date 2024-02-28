"""This example is a parallelism example from LangChain documentation using mirascope

https://python.langchain.com/docs/expression_language/how_to/map#parallelize-steps

The example uses Mirascope Prompts to validate the inputs and easily generate the invoke
arguments for the chain.
"""
import os

from langchain_config import Settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

from mirascope import Prompt

settings = Settings()
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class JokePrompt(Prompt):
    """tell me a joke about {topic}"""

    topic: str


class PoemPrompt(Prompt):
    """write a 2-line poem about {topic}"""

    topic: str


model = ChatOpenAI()
joke_prompt = JokePrompt(topic="bear")
poem_prompt = PoemPrompt(topic="bear")

joke_chain = ChatPromptTemplate.from_template(joke_prompt.template()) | model
poem_chain = ChatPromptTemplate.from_template(poem_prompt.template()) | model

map_chain = RunnableParallel(joke=joke_chain, poem=poem_chain)
invoke = joke_prompt.model_dump() | poem_prompt.model_dump()

print(map_chain.invoke(invoke))
