"""
Dumping makes it easy to log your LLM calls
"""
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


def log_to_database(recommender_response_dump: dict[str, Any]):
    """Create a recommender response dump and log it to the database."""
    create_database()
    Session = sessionmaker(engine)
    with Session() as session:
        openai_completion_db = OpenAIChatCompletionTable(**recommender_response_dump)
        session.add(openai_completion_db)
        session.commit()


def log_to_csv(recommender_response_dump: dict[str, Any]):
    """Log the recommender response dump to a CSV file."""
    df = pd.DataFrame([recommender_response_dump])
    with open("log.csv", "w") as f:
        df.to_csv(f, index=False)


def log_to_logger(recommender_response_dump: dict[str, Any]):
    """Log the recommender response dump to the logger."""
    logger.info(recommender_response_dump)


if __name__ == "__main__":
    recommender = BookRecommender(topic="how to bake a cake")
    response = recommender.call()
    recommender_response_dump = recommender.dump() | response.dump()
    log_to_database(recommender_response_dump)
    log_to_csv(recommender_response_dump)
    log_to_logger(recommender_response_dump)
