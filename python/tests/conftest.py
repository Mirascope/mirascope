"""Configuration for all Mirascope tests."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Generator

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session")
def gcp_credentials_file() -> Generator[str, None, None]:
    """Create temporary GCP service account credentials file for testing.

    Anthropic Vertex client initializes anthropic.lib.vertex._auth.load_auth()
    which calls google.auth.default(...) to resolve Application Default Credentials.
    Without real ADC in CI, this fails with DefaultCredentialsError or metadata
    server access errors.

    This fixture creates a dummy service account JSON file and sets
    GOOGLE_APPLICATION_CREDENTIALS to satisfy google-auth's file requirements.
    Combined with NO_GCE_CHECK=True, this prevents metadata server checks.

    Note that Google Gemini uses simple API key authentication and does not
    require ADC, which is why this complexity is only needed for Vertex AI.

    Yields:
        Path to temporary credentials JSON file
    """
    credentials = {
        "type": "service_account",
        "project_id": "dummy-gcp-project",
        "private_key_id": "dummy-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUJrfv8F3tDNnC\nTZWQp2AArELcU1sQC8u7R+Py+32a7Kshdd17imJ0X80BNFULIKbv4RzAu5k5bAI8\nL5ctUgEUff8wh67doglynRebbQ0ykGEVE3t3BuoPt9HFHFV2J7d6IFZ6INNJ18hF\nnIjx3EXQJkG3GKRpv9t/uriYCQmrkxWbnNxsbYtwf5MRqH6fnWtFGxWU2yaFhEpx\n3cTmCLDPLvNJS/3JaonBeXPu4f1i5cfbgxIErsHzKU7S9vwWOmriOMYmcGgexVZJ\nMEL3h6hhTQ5BZ3YLVSGxU+SS/xDgeJRvPI2rf/XjsjeoJTxfUnaa7N05ZMh6qxH9\nkdxem7p1AgMBAAECggEARUn6BEMYoi3yxyuowCxyRfX9BlGxKa34lcu2jusFjH5k\nrBJ/SnSZkFGjtpN9fRtmem0nA2mh8yesGTUf5nzkfmliWdrOyXM9K7JT/f7hcxTF\nqGkLB4Z6FrUeLYcCAIubOKdsJwomh/USY23rKjcblA6SovbI6ALx8ScuV/WHs4HH\ngLCrmTUcvM5I5fwFeiw8ormAvSgAwPC7cC7cFSHIWvXVb2wXiqVO6td+JC+1qqMa\nedu9Tk33ath3sMEThg2/M00tUy7r/HTP2BtbIneMTzt3pGxdMlApn12VlXFwhVib\ngq3ojOimMHb0vhuHu8NFFiAIwrJMd/5Z1jyg7Jb4twKBgQD0x4Rgn2t/sCD6OLoA\nmtiqI+quW/SHPp4sUQhzogumJkefJA21IK2M0qr6pI0gV4K918aKU1cLy2KQB3xH\n6G4RkaDP0P6mFmSTY/YTvN62Q2h1XcjSxlTxASL/VOhzcjkCqWkyHCi0qmZoEhX6\ntMhflpPw4JHpDE7QxNg9hgvxYwKBgQDd4E+RgP44JfhmyohY87LuH78Iqe7SaDU8\nNwQEuh0vP7G/qeqX6/9m1nZ7yCpe+AnGByFq4uVjZMrMoUlv1NLk3V2PPs6SgTaa\ntd/16A+xEwq1p4zMP6sQn3TSz8rAob2yRuHPBmIhni2ICkK8FI3AYp8VIla5lflx\nQ6aq8/OYRwKBgQCUXksS9g6Guw+CG9hCfZlOp66cOQii4YWmfweMb3B4KUPIZmYY\nn9ISRa91dUBFlkWdJKknNxTQBVucyay/OVdeNtMupBN2QKR94l1J4XVtLLaoTUxo\n1eaunm3ELocnUtjTkDQ/N2pE9/RSqIPCDspVhkPuAXDvvZIYYPhhclrS2QKBgQCC\n9+5f6DGnuRoYqwKy5x8+mnSsS4rSnnqWEa+Ijse9ZS6qAUWd6ct3y65iwLPqHSW/\nw+PA8TAQbKWdBrOPlKPsPpMEhEFxj15JEoSh5hqlHqVatw1QX2C9zjIqYke/T3nn\nKxoNlyoDyBf+Tng4BzXpUw2ubvecUt/MMO/Hx3qJ7wKBgHyh72O4sej+P4gp6xiq\n9+QWcDnlkRQUyXp0ZEaHSrXBMiEENydqikr3yQboT3D0g4QLkuh7xoce3bWKo8Y1\nCemdPpFG7AsDw44UKc21tmS+5x/6xExQnou4crly6pCNJUVBpgYQPaeS6LBNlOM1\nVNarZ+D1oOeo58KiTHoGG+CI\n-----END PRIVATE KEY-----\n",
        "client_email": "dummy@dummy-gcp-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy%40dummy-gcp-project.iam.gserviceaccount.com",
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as temp_file:
        json.dump(credentials, temp_file)
        temp_path = temp_file.name

    yield temp_path

    os.unlink(temp_path)


@pytest.fixture(scope="session", autouse=True)
def load_api_keys(gcp_credentials_file: str) -> None:
    """Load environment variables from .env file.

    This is necessary for e2e tests, but also may be necessary for any tests that
    instantiate a client, as clients may test API key presence at `__init__` time.

    Sets dummy API keys and credentials for CI environments, and configures NO_GCE_CHECK
    to prevent Google auth from attempting to reach the GCE metadata server during tests.

    Args:
        gcp_credentials_file: Path to temporary GCP credentials file
    """
    load_dotenv()
    # Set dummy keys if not present so that tests pass in CI.
    os.environ.setdefault("ANTHROPIC_API_KEY", "dummy-anthropic-key")
    os.environ.setdefault("GOOGLE_API_KEY", "dummy-google-key")
    os.environ.setdefault("OPENAI_API_KEY", "dummy-openai-key")
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

    os.environ.setdefault("CLOUD_ML_REGION", "us-east5")
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "dummy-gcp-project")
    os.environ.setdefault("NO_GCE_CHECK", "True")
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", gcp_credentials_file)
