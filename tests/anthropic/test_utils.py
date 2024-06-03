"""Tests for Mirascope's Anthropic utils module."""

from anthropic import Anthropic, AnthropicBedrock, AsyncAnthropic, AsyncAnthropicBedrock

from mirascope.anthropic.utils import bedrock_client_wrapper


def test_bedrock_client_wrapper():
    """Tests the Anthropic client wrapper for AWS Bedrock."""
    kwargs = {
        "aws_secret_key": "TEST_SECRET_KEY",
        "aws_access_key": "TEST_ACCESS_KEY",
        "aws_region": "us-west-2",
        "aws_session_token": "TEST_SESSION_TOKEN",
        "base_url": "TEST_BASE_URL/",
    }
    wrapper = bedrock_client_wrapper(**kwargs)
    client = Anthropic()
    wrapped_client = wrapper(client)
    assert isinstance(wrapped_client, AnthropicBedrock)
    async_client = AsyncAnthropic()
    wrapped_async_client = wrapper(async_client)
    assert isinstance(wrapped_async_client, AsyncAnthropicBedrock)
    for key, value in kwargs.items():
        assert getattr(wrapped_client, key) == value
        assert getattr(wrapped_async_client, key) == value
