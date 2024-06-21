"""Logging your LLM responses to a postgres database"""

import os
from typing import Literal, Optional

from sqlalchemy import Float, Integer, MetaData, String, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
TABLE_NAME = "openai_chat_completions"


class Base(DeclarativeBase):
    pass


class OpenAIChatCompletionTable(Base):
    __tablename__ = TABLE_NAME
    id: Mapped[int] = mapped_column(
        Integer(), primary_key=True, autoincrement=True, nullable=False
    )
    prompt_template: Mapped[str] = mapped_column(String(), nullable=False)
    fn_args: Mapped[Optional[dict]] = mapped_column(JSONB)
    fn_return: Mapped[Optional[dict]] = mapped_column(JSONB)
    messages: Mapped[Optional[list[dict]]] = mapped_column(JSONB)
    call_params: Mapped[Optional[dict]] = mapped_column(JSONB)
    start_time: Mapped[Optional[float]] = mapped_column(Float(), nullable=False)
    end_time: Mapped[Optional[float]] = mapped_column(Float(), nullable=False)
    cost: Mapped[Optional[float]] = mapped_column(Float())
    response: Mapped[Optional[dict]] = mapped_column(JSONB)
    tool_types: Mapped[Optional[list[dict]]] = mapped_column(JSONB)
    tools: Mapped[Optional[list[dict]]] = mapped_column(JSONB)
    tool: Mapped[Optional[dict]] = mapped_column(JSONB)
    user_message_param: Mapped[Optional[dict]] = mapped_column(JSONB)
    message_param: Mapped[Optional[dict]] = mapped_column(JSONB)


def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
):
    """Get the current weather in a given location."""
    if "tokyo" in location.lower():
        print(f"It is 10 degrees {unit} in Tokyo, Japan")
    elif "san francisco" in location.lower():
        print(f"It is 72 degrees {unit} in San Francisco, CA")
    elif "paris" in location.lower():
        print(f"It is 22 degress {unit} in Paris, France")
    else:
        print("I'm not sure what the weather is like in {location}")


@openai.call(model="gpt-4o", tools=[get_current_weather])
def forecast(location: str):
    """What's the weather in {location}?"""


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


response = forecast(location="tokyo")
# create_database()  # ONE TIME ONLY
Session = sessionmaker(engine)
with Session() as session:
    openai_completion_db = OpenAIChatCompletionTable(**response.model_dump())
    session.add(openai_completion_db)
    session.commit()
