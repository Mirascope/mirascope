"""Tests the `openai.add_batch` module."""

import json
import os
import uuid
from unittest.mock import MagicMock, mock_open, patch

from mirascope.core import openai


@patch("builtins.open", new_callable=mock_open, read_data="data")
@patch("openai.OpenAI", new_callable=MagicMock())
def test_openai_run_batch(mock_openai: MagicMock, mock_file) -> None:
    mock_create = mock_openai.return_value.files.create
    mock_batch_create = mock_openai.return_value.batches.create
    mock_create.return_value.id = "batch_id"

    batch_filename = f"/tmp/batch_job_{uuid.uuid4()}.jsonl"
    batch = [
        {
            "custom_id": "task-0",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [{"content": "Recommend a fantasy book", "role": "user"}],
            },
        },
        {
            "custom_id": "task-1",
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

    with open(batch_filename, "w") as f:
        for b in batch:
            f.write(json.dumps(b) + "\n")

    openai.run_batch(batch_filename)

    mock_create.assert_called_once_with(file=mock_file(), purpose="batch")
    mock_batch_create.assert_called_once_with(
        input_file_id="batch_id",
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    if os.path.exists(batch_filename):
        os.remove(batch_filename)
