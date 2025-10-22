"""Configuration for all Mirascope tests."""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_api_keys() -> None:
    """Load environment variables from .env file.

    This is necessary for e2e tests, but also may be necessary for any tests that
    instantiate a client, as clients may test API key presence at `__init__` time.
    """
    load_dotenv()
    # Set dummy keys if not present so that tests pass in CI.
    os.environ.setdefault("ANTHROPIC_API_KEY", "dummy-anthropic-key")
    os.environ.setdefault("GOOGLE_API_KEY", "dummy-google-key")
    os.environ.setdefault("OPENAI_API_KEY", "dummy-openai-key")
    # Azure OpenAI requires both API key and endpoint
    os.environ.setdefault("AZURE_OPENAI_API_KEY", "dummy-azure-openai-key")
    os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://dummy.openai.azure.com")

    # AWS Bedrock credentials: prefer ~/.aws/credentials file over dummy values
    # Only set dummy credentials if ~/.aws/credentials doesn't exist
    aws_credentials_path = os.path.expanduser("~/.aws/credentials")
    if not os.path.isfile(aws_credentials_path):
        os.environ.setdefault("AWS_ACCESS_KEY_ID", "dummy-aws-access-key")
        os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "dummy-aws-secret-key")

    # Always set default region if not already set
    os.environ.setdefault("AWS_REGION", "us-east-1")
