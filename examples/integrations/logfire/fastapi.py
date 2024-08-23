import logfire
from fastapi import FastAPI
from pydantic import BaseModel

from mirascope.core import openai, prompt_template
from mirascope.integrations.logfire import with_logfire

app = FastAPI()
logfire.configure()
logfire.instrument_fastapi(app)


class Book(BaseModel):
    title: str
    author: str


@app.post("/")
@with_logfire()
@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...
