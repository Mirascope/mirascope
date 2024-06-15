"""
Logging your LLM responses to a postgres database
"""
import os
from typing import Optional

from sqlalchemy import JSON, Float, Integer, MetaData, String, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from mirascope import tags
from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

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
class BookRecommender(OpenAICall):
    prompt_template = """
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


recommender = BookRecommender(topic="how to bake a cake")
response = recommender.call()
recommender_response_dump = recommender.dump() | response.dump()
create_database()  # ONE TIME ONLY
Session = sessionmaker(engine)
with Session() as session:
    openai_completion_db = OpenAIChatCompletionTable(**recommender_response_dump)
    session.add(openai_completion_db)
    session.commit()
