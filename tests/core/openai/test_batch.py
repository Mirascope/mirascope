"""Tests the `openai.add_batch` module."""

import json
import os
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch
from uuid import UUID, uuid4

from mirascope.core import prompt_template
from mirascope.core.openai import OpenAIBatch


@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


class OpenAIBatchTests(TestCase):
    def test_openai_call_add_batch_creates(self) -> None:
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
                    "messages": [
                        {"content": "Recommend a fantasy book", "role": "user"}
                    ],
                },
            },
            {
                "custom_id": f"task-{expected_uuid}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"content": "Recommend a horror book", "role": "user"}
                    ],
                },
            },
        ]

        if os.path.exists(batch_filename):
            os.remove(batch_filename)

        with patch("uuid.uuid4") as mock_uuid4:
            mock_uuid4.return_value = expected_uuid
            batch = OpenAIBatch(batch_filename)
            batch.add(recommend_book, "gpt-4o-mini", data_genres)

        with open(batch_filename) as f:
            assert (
                json.dumps(expected[0]) + "\n" + json.dumps(expected[1]) + "\n"
                == f.read()
            )

        if os.path.exists(batch_filename):
            os.remove(batch_filename)

    def test_openai_call_add_batch_appends(self) -> None:
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
            batch = OpenAIBatch(batch_filename)
            batch.add(recommend_book, "gpt-4o-mini", data_genres)

        with open(batch_filename) as f:
            assert json.dumps(expected) + "\n" + json.dumps(expected) + "\n" == f.read()

        if os.path.exists(batch_filename):
            os.remove(batch_filename)

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch("mirascope.core.openai.batch.OpenAI", new_callable=MagicMock())
    def test_openai_run_batch(self, mock_openai: MagicMock, mock_file) -> None:
        mock_create = mock_openai.return_value.files.create
        mock_batch_create = mock_openai.return_value.batches.create
        mock_create.return_value.id = "batch_id"

        batch_filename = f"/tmp/batch_job_{uuid4()}.jsonl"
        batch = [
            {
                "custom_id": "task-0",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"content": "Recommend a fantasy book", "role": "user"}
                    ],
                },
            },
            {
                "custom_id": "task-1",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"content": "Recommend a horror book", "role": "user"}
                    ],
                },
            },
        ]

        if os.path.exists(batch_filename):
            os.remove(batch_filename)

        with open(batch_filename, "w") as f:
            for b in batch:
                f.write(json.dumps(b) + "\n")

        batch = OpenAIBatch(batch_filename)
        batch.run()

        mock_create.assert_called_once_with(file=mock_file(), purpose="batch")
        mock_batch_create.assert_called_once_with(
            input_file_id="batch_id",
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        if os.path.exists(batch_filename):
            os.remove(batch_filename)

    @patch("builtins.open", new_callable=mock_open, read_data='{"some": "result"}')
    @patch("mirascope.core.openai.batch.OpenAI", new_callable=MagicMock())
    def test_openai_retrieve_batch(self, mock_openai: MagicMock, mock_file) -> None:
        mock_content = mock_openai.return_value.files.content
        mock_batch_create = mock_openai.return_value.batches.create
        mock_batch_create.return_value.id = "batch_id"
        mock_retrieve = mock_openai.return_value.batches.retrieve
        mock_content.return_value.content = "content"
        mock_retrieve.return_value.status = "completed"
        mock_retrieve.return_value.output_file_id = "some-output-file-id"

        batch = OpenAIBatch()
        batch.run()
        results = batch.retrieve(result_file_name="test.jsonl")

        mock_retrieve.assert_called_once_with("batch_id")
        mock_content.assert_called_once_with("some-output-file-id")
        mock_file.assert_called()
        assert results == [{"some": "result"}]
