import sqlite3
from typing import ClassVar
from unittest.mock import MagicMock

import pytest

from examples.cookbook.agents.sql_agent.agent import Librarian


@pytest.fixture
def mock_librarian():
    class MockLibrarian(Librarian):
        con: ClassVar[sqlite3.Connection] = MagicMock()

    return MockLibrarian()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "select_query",
    [
        "Get all books",
        "Get every single book",
        "Show me all books",
        "List all books",
        "Display all books",
    ],
)
async def test_select_query(select_query: str, mock_librarian: Librarian):
    response = await mock_librarian._step(select_query)
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert query == "SELECT * FROM ReadingList;"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "insert_query",
    [
        "Please add Gone with the Wind to my reading list",
        "You recently recommended Gone with the Wind, can you add it to my reading list.",
    ],
)
async def test_insert_query(insert_query: str, mock_librarian: Librarian):
    response = await mock_librarian._step(insert_query)
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert (
            query
            == "INSERT INTO ReadingList (title, status) VALUES ('Gone with the Wind', 'Not Started');"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_query",
    [
        "Can you mark Gone with the Wind as read.",
        "I just finished Gone with the Wind, can you update the status?",
    ],
)
async def test_update_query(update_query: str, mock_librarian: Librarian):
    response = await mock_librarian._step(update_query)
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert (
            query
            == "UPDATE ReadingList SET status = 'Complete' WHERE title = 'Gone with the Wind';"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "delete_query",
    [
        "Can you remove Gone with the Wind from my reading list?",
        "Can you delete Gone with the Wind?",
    ],
)
async def test_delete_query(delete_query: str, mock_librarian: Librarian):
    response = await mock_librarian._step(delete_query)
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert query == "DELETE FROM ReadingList WHERE title = 'Gone with the Wind';"
