"""This example is a simple RAG example from LangChain documentation using mirascope

https://python.langchain.com/docs/expression_language/get_started#rag-search-example

Since LangChain's example uses Pydantic V1 for vectorstore this example uses a basic 
context but a more advanced implementation of context can be found in 
https://docs.mirascope.io/latest/cookbook/rag/.
"""

import os
from typing import Union

from langchain_config import Settings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI

from mirascope import BasePrompt

settings = Settings()

os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class QuestionPrompt(BasePrompt):
    """
    Answer the question based only on the following context:
    {context}

    Question:
    {question}
    """

    context: Union[list[str], str]
    question: str


context = ["harrison worked at kensho", "bears like to eat honey"]
question_prompt = QuestionPrompt(context=context, question="where did harrison work?")
prompt = ChatPromptTemplate.from_template(question_prompt.template())
model = ChatOpenAI()
output_parser = StrOutputParser()

chain = prompt | model | output_parser

print(chain.invoke(question_prompt.model_dump()))
