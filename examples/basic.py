"""Basic Prompt + LLM Example Using LangChain."""

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

from prompts import JokePrompt

prompt = ChatPromptTemplate.from_template(JokePrompt.template())
model = ChatOpenAI()
chain = prompt | model

chain = prompt | model.bind(stop=["\n"]) | StrOutputParser()
print(chain.invoke(JokePrompt(foo="bears").__dict__))
