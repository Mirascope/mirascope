from __future__ import annotations

from aiobotocore.session import get_session
from boto3.session import Session
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from types_aiobotocore_bedrock_runtime import (
    BedrockRuntimeClient as AsyncBedrockRuntimeClient,
)


def _get_sync_client() -> BedrockRuntimeClient:
    session = Session()
    return session.client("bedrock-runtime")


async def _get_async_client() -> AsyncBedrockRuntimeClient:
    session = get_session()
    async with session.create_client("bedrock-runtime") as client:
        return client
