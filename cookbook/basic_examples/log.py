"""A basic example on how to log the data from a prompt and a chat completion."""
import logging
import os
from typing import Optional

import pandas as pd
from sqlalchemy import JSON, Float, Integer, MetaData, String, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from mirascope import OpenAIChat, Prompt, tags

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
    start_time: Mapped[Optional[float]] = mapped_column(Float(), nullable=False)
    end_time: Mapped[Optional[float]] = mapped_column(Float(), nullable=False)
    output: Mapped[Optional[dict]] = mapped_column(JSONB)


@tags(["recommendation_project"])
class BookRecommendationPrompt(Prompt):
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


def log_to_database(prompt_completion: dict):
    """Create a prompt completion and log it to the database."""
    create_database()
    Session = sessionmaker(engine)
    with Session() as session:
        openai_completion_db = OpenAIChatCompletionTable(**prompt_completion)
        session.add(openai_completion_db)
        session.commit()


def log_to_csv(prompt_completion: dict):
    """Log the prompt completion to a CSV file."""
    df = pd.DataFrame([prompt_completion])
    with open("log.csv", "w") as f:
        df.to_csv(f, index=False)


def log_to_logger(prompt_completion: dict):
    """Log the prompt completion to the logger."""
    logger.info(prompt_completion)


if __name__ == "__main__":
    prompt = BookRecommendationPrompt(topic="how to bake a cake")
    model = OpenAIChat()
    completion = model.create(prompt)
    prompt_completion = prompt.dump(completion)
    log_to_database(prompt_completion)
    log_to_csv(prompt_completion)
    log_to_logger(prompt_completion)
