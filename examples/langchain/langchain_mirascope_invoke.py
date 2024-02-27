"""This example is a simple invoke from LangChain documentation using mirascope

https://python.langchain.com/docs/expression_language/get_started
#basic-example-prompt-model-output-parser

The example uses Mirascope Prompts to validate the inputs and easily generate the invoke
arguments for the chain.
"""

import os

from config import Settings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from mirascope import Prompt

settings = Settings()
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class TellMeAJokePrompt(Prompt):
    """
    tell me a short joke about {topic}
    """

    topic: str


joke_prompt = TellMeAJokePrompt(topic="ice cream")
prompt = ChatPromptTemplate.from_template(joke_prompt.template())
model = ChatOpenAI(model="gpt-4")
output_parser = StrOutputParser()

chain = prompt | model | output_parser

print(chain.invoke(joke_prompt.model_dump()))
