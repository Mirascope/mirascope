from unittest.mock import MagicMock, patch

import pytest
from azure.core.credentials import AzureKeyCredential

from mirascope.core.azure._utils._get_credential import (
    _get_azure_default_credential,
    _get_key_from_env,
    get_credential,
)


@pytest.mark.parametrize(
    "env_value, expected",
    [
        ("test_key", "test_key"),
        (None, None),
    ],
)
def test_get_key_from_env(env_value, expected):
    with patch("os.environ.get", return_value=env_value):
        assert _get_key_from_env() == expected


def test_get_azure_default_credential_success():
    mock_instance = MagicMock()

    with patch(
        "azure.identity.DefaultAzureCredential"
    ) as mock_default_azure_credential:
        mock_default_azure_credential.return_value = mock_instance
        result = _get_azure_default_credential()
        assert result == mock_instance
        mock_default_azure_credential.assert_called_once()


def test_get_azure_default_credential_import_error():
    with patch.dict("sys.modules", {"azure.identity": None}):
        with pytest.raises(ImportError) as exc_info:
            _get_azure_default_credential()
        assert "please install the azure-identity package" in str(exc_info.value)


@pytest.mark.parametrize(
    "key_value, expected_type",
    [
        ("test_key", AzureKeyCredential),
        (None, MagicMock),  # DefaultAzureCredential will be mocked
    ],
)
def test_get_credential(key_value, expected_type):
    with patch(
        "mirascope.core.azure._utils._get_credential._get_key_from_env",
        return_value=key_value,
    ):
        if key_value is None:
            with patch(
                "mirascope.core.azure._utils._get_credential._get_azure_default_credential"
            ) as mock_default_cred:
                mock_default_cred.return_value = MagicMock(spec=object)
                result = get_credential()
                assert isinstance(result, expected_type)
                mock_default_cred.assert_called_once()
        else:
            result = get_credential()
            assert isinstance(result, expected_type)
            assert result.key == key_value  # pyright: ignore [reportAttributeAccessIssue]
