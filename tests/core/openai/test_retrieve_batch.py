from unittest.mock import MagicMock, mock_open, patch

from mirascope.core import openai


@patch("builtins.open", new_callable=mock_open, read_data='{"some": "result"}')
@patch("openai.OpenAI", new_callable=MagicMock())
def test_openai_retrieve_batch(mock_openai: MagicMock, mock_file) -> None:
    mock_content = mock_openai.return_value.files.content
    mock_retrieve = mock_openai.return_value.batches.retrieve
    mock_content.return_value.content = "content"
    mock_retrieve.return_value.status = "completed"
    mock_retrieve.return_value.output_file_id = "some-output-file-id"

    results = openai.retrieve_batch(
        batch_job=MagicMock(id="some-id"), result_file_name="test.jsonl"
    )

    mock_retrieve.assert_called_once_with("some-id")
    mock_content.assert_called_once_with("some-output-file-id")
    mock_file.assert_called()
    assert results == [{"some": "result"}]
