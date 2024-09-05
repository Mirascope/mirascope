from __future__ import annotations

import os
from typing import TYPE_CHECKING

from azure.core.credentials import AzureKeyCredential

if TYPE_CHECKING:
    from azure.identity import (  # pyright: ignore [reportMissingImports]
        DefaultAzureCredential,
    )
else:
    AzureDefaultCredential = None


def _get_key_from_env() -> str | None:
    return os.environ.get("AZURE_INFERENCE_CREDENTIAL")


def _get_azure_default_credential() -> DefaultAzureCredential:
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError:
        raise ImportError(
            "To use the AzureDefaultCredential, please install the azure-identity package with `pip install azure-identity`."
        )
    return DefaultAzureCredential()


def get_credential() -> DefaultAzureCredential | AzureKeyCredential:
    if (credential := _get_key_from_env()) is None:
        return _get_azure_default_credential()
    return AzureKeyCredential(credential)
