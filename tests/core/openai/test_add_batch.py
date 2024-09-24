"""Tests the `openai.add_batch` module."""

import json
import os
from unittest.mock import patch
from uuid import UUID, uuid4

from mirascope.core import openai, prompt_template


@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


def test_openai_call_add_batch_creates() -> None:
    data_genres = ["fantasy", "horror"]
    expected_uuid = UUID("87654321-4321-8765-4321-876543218765")
    batch_filename = f"/tmp/batch_job_{uuid4()}.jsonl"
    expected = [
        {
            "custom_id": f"task-{expected_uuid}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [{"content": "Recommend a fantasy book", "role": "user"}],
            },
        },
        {
            "custom_id": f"task-{expected_uuid}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [{"content": "Recommend a horror book", "role": "user"}],
            },
        },
    ]

    if os.path.exists(batch_filename):
        os.remove(batch_filename)

    with patch("uuid.uuid4") as mock_uuid4:
        mock_uuid4.return_value = expected_uuid
        openai.add_batch(recommend_book, "gpt-4o-mini", data_genres, batch_filename)

    with open(batch_filename) as f:
        assert (
            json.dumps(expected[0]) + "\n" + json.dumps(expected[1]) + "\n" == f.read()
        )

    if os.path.exists(batch_filename):
        os.remove(batch_filename)


def test_openai_call_add_batch_appends() -> None:
    data_genres = ["fantasy"]
    expected_uuid = UUID("87654321-4321-8765-4321-876543218765")
    batch_filename = f"/tmp/batch_job_{uuid4()}.jsonl"
    expected = {
        "custom_id": f"task-{expected_uuid}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [{"content": "Recommend a fantasy book", "role": "user"}],
        },
    }

    if os.path.exists(batch_filename):
        os.remove(batch_filename)

    with open(batch_filename, "w") as f:
        f.write(json.dumps(expected) + "\n")

    with patch("uuid.uuid4") as mock_uuid4:
        mock_uuid4.return_value = expected_uuid
        openai.add_batch(recommend_book, "gpt-4o-mini", data_genres, batch_filename)

    with open(batch_filename) as f:
        assert json.dumps(expected) + "\n" + json.dumps(expected) + "\n" == f.read()

    if os.path.exists(batch_filename):
        os.remove(batch_filename)
