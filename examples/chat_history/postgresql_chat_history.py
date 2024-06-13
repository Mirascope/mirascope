"""
This example demonstrates how to use the chat history feature with a PostgreSQL database.

While most RAG solutions use vector databases, this example uses 
a traditional relational database.

Setup:
pip install sqlalchemy
pip install psycopg2
pip install mirascope
"""
import os
from typing import Literal, cast

from anthropic.types import MessageParam
from sqlalchemy import Integer, MetaData, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from mirascope.anthropic import AnthropicCall

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

# Postgres + SQLAlchemy setup
TABLE_NAME = "table_name"
USERNAME = "root"
PASSWORD = ""
HOST = "localhost"
PORT = "5432"
DB_NAME = "db_name"


class Base(DeclarativeBase):
    pass


class Messages(Base):
    __tablename__ = TABLE_NAME
    id: Mapped[int] = mapped_column(
        Integer(), primary_key=True, autoincrement=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(), nullable=False)
    content: Mapped[str] = mapped_column(String(), nullable=False)


engine = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}")


def create_database():
    """Create the database and table for the OpenAI chat completions."""
    metadata = MetaData()
    table_objects = [Base.metadata.tables[TABLE_NAME]]
    metadata.create_all(engine, tables=table_objects)


# ONE TIME CREATION OF THE DATABASE AND TABLE
# create_database()


# Mirascope OpenAI librarian chat app
class Librarian(AnthropicCall):
    prompt_template = """
	SYSTEM: You are the world's greatest librarian.
	MESSAGES: {history}
	USER: {question}
	"""

    question: str

    @property
    def history(self) -> list[MessageParam]:
        with Session() as session:
            chat_history = session.query(Messages).all()
            return [
                {
                    "role": cast(Literal["user", "assistant"], chat.role),
                    "content": chat.content,
                }
                for chat in chat_history
            ]


Session = sessionmaker(engine)
librarian = Librarian(question="")
with Session() as session:
    while True:
        librarian.question = input("(User): ")
        if librarian.question == "exit":
            break
        response = librarian.call()
        session.add(Messages(role="user", content=librarian.question))
        session.add(Messages(role="assistant", content=response.content))
        session.commit()
        print(f"(Assistant): {response.content}")
