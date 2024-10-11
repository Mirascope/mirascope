"""Test configuration fixtures used bedrock module."""

import os

import pytest


@pytest.fixture(autouse=True)
def aws_default_region():
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
