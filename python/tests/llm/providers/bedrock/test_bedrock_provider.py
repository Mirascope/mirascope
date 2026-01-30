"""Tests for BedrockProvider routing."""

import builtins
import sys
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from mirascope import llm
from mirascope.llm.messages import user
from mirascope.llm.providers.bedrock import BedrockProvider
from mirascope.llm.providers.bedrock._utils import (
    bedrock_model_name,
    default_anthropic_scopes,
)
from mirascope.llm.providers.bedrock.provider import (
    _default_routing_scopes,  # pyright: ignore[reportPrivateUsage]
    _is_anthropic_arn,  # pyright: ignore[reportPrivateUsage]
)

EMPTY_TOOLKIT = llm.Toolkit(None)


def test_bedrock_model_name_strips_prefix() -> None:
    """Test bedrock_model_name strips 'bedrock/' prefix."""
    assert (
        bedrock_model_name("bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0")
        == "anthropic.claude-3-5-sonnet-20241022-v1:0"
    )


def test_bedrock_model_name_preserves_non_prefixed() -> None:
    """Test bedrock_model_name preserves model IDs without prefix."""
    assert (
        bedrock_model_name("anthropic.claude-3-5-sonnet-20241022-v1:0")
        == "anthropic.claude-3-5-sonnet-20241022-v1:0"
    )


def test_bedrock_model_name_preserves_inference_profile() -> None:
    """Test bedrock_model_name handles inference profile IDs."""
    assert (
        bedrock_model_name("bedrock/us.anthropic.claude-3-5-sonnet-20241022-v1:0")
        == "us.anthropic.claude-3-5-sonnet-20241022-v1:0"
    )


def test_default_anthropic_scopes_contains_base_prefix() -> None:
    """Test default_anthropic_scopes includes base model prefix."""
    scopes = default_anthropic_scopes()
    assert "bedrock/anthropic." in scopes


def test_default_anthropic_scopes_contains_regional_prefixes() -> None:
    """Test default_anthropic_scopes includes regional inference profile prefixes."""
    scopes = default_anthropic_scopes()
    assert "bedrock/us.anthropic." in scopes
    assert "bedrock/eu.anthropic." in scopes
    assert "bedrock/apac.anthropic." in scopes
    assert "bedrock/global.anthropic." in scopes


def test_default_anthropic_scopes_excludes_generic_arn_prefix() -> None:
    """Test default_anthropic_scopes does not include generic ARN prefix.

    ARN routing is handled separately by _is_anthropic_arn() to avoid
    matching non-Anthropic ARNs via prefix matching.
    """
    scopes = default_anthropic_scopes()
    assert "bedrock/arn:aws:bedrock:" not in scopes


def test_default_routing_scopes_has_anthropic() -> None:
    """Test _default_routing_scopes has anthropic key."""
    scopes = _default_routing_scopes()
    assert "anthropic" in scopes
    assert len(scopes["anthropic"]) > 0


@pytest.mark.parametrize(
    "arn",
    [
        "bedrock/arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v1:0",
        "bedrock/arn:aws-us-gov:bedrock:us-gov-west-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v1:0",
        "bedrock/arn:aws-cn:bedrock:cn-north-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v1:0",
    ],
)
def test_is_anthropic_arn_detects_anthropic_arns(arn: str) -> None:
    """Test _is_anthropic_arn detects Anthropic ARNs across partitions."""
    assert _is_anthropic_arn(arn) is True


@pytest.mark.parametrize(
    "arn",
    [
        "bedrock/arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0",
        "bedrock/arn:aws-us-gov:bedrock:us-gov-west-1::foundation-model/amazon.nova-lite-v1:0",
        "bedrock/arn:aws-cn:bedrock:cn-north-1::foundation-model/amazon.nova-lite-v1:0",
    ],
)
def test_is_anthropic_arn_rejects_non_anthropic_arns(arn: str) -> None:
    """Test _is_anthropic_arn returns False for non-Anthropic ARNs."""
    assert _is_anthropic_arn(arn) is False


def test_is_anthropic_arn_non_arn() -> None:
    """Test _is_anthropic_arn returns False for non-ARN model IDs."""
    assert (
        _is_anthropic_arn("bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0") is False
    )


def test_is_anthropic_arn_non_bedrock_service() -> None:
    """Test _is_anthropic_arn returns False for non-Bedrock service ARNs."""
    arn = "bedrock/arn:aws:sagemaker:us-east-1:123456789012:endpoint/my-endpoint"
    assert _is_anthropic_arn(arn) is False


def test_bedrock_provider_initialization() -> None:
    """Test BedrockProvider initialization with default settings."""
    provider = BedrockProvider()
    assert provider.id == "bedrock"
    assert provider.default_scope == "bedrock/"
    assert provider._routing_scopes is not None  # pyright: ignore[reportPrivateUsage]


def test_bedrock_provider_initialization_with_aws_credentials() -> None:
    """Test BedrockProvider initialization with AWS credentials."""
    provider = BedrockProvider(
        aws_region="us-east-1",
        aws_access_key="test-access-key",
        aws_secret_key="test-secret-key",
        aws_session_token="test-session-token",
    )
    assert provider._aws_region == "us-east-1"  # pyright: ignore[reportPrivateUsage]
    assert provider._aws_access_key == "test-access-key"  # pyright: ignore[reportPrivateUsage]
    assert provider._aws_secret_key == "test-secret-key"  # pyright: ignore[reportPrivateUsage]
    assert provider._aws_session_token == "test-session-token"  # pyright: ignore[reportPrivateUsage]


def test_bedrock_provider_initialization_with_routing_scopes() -> None:
    """Test BedrockProvider initialization with custom routing scopes."""
    provider = BedrockProvider(
        routing_scopes={"anthropic": ["bedrock/custom-prefix."]},
    )
    assert "bedrock/custom-prefix." in provider._routing_scopes["anthropic"]  # pyright: ignore[reportPrivateUsage]


def test_bedrock_provider_get_error_status() -> None:
    """Test BedrockProvider get_error_status returns status code."""
    provider = BedrockProvider()

    class DummyError(Exception):
        status_code = 418

    assert provider.get_error_status(DummyError()) == 418


def test_bedrock_provider_route_anthropic_base_model() -> None:
    """Test BedrockProvider routes Anthropic base model IDs."""
    provider = BedrockProvider()
    route = provider._route_provider(  # pyright: ignore[reportPrivateUsage]
        "bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0"
    )
    assert route == "anthropic"


def test_bedrock_provider_route_anthropic_inference_profile() -> None:
    """Test BedrockProvider routes Anthropic inference profile IDs."""
    provider = BedrockProvider()
    route = provider._route_provider(  # pyright: ignore[reportPrivateUsage]
        "bedrock/us.anthropic.claude-3-5-sonnet-20241022-v1:0"
    )
    assert route == "anthropic"


def test_bedrock_provider_route_anthropic_arn() -> None:
    """Test BedrockProvider routes Anthropic foundation model ARNs."""
    provider = BedrockProvider()
    arn = "bedrock/arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v1:0"
    route = provider._route_provider(arn)  # pyright: ignore[reportPrivateUsage]
    assert route == "anthropic"


def test_bedrock_provider_route_non_anthropic_arn_returns_none() -> None:
    """Test BedrockProvider returns None for non-Anthropic ARNs."""
    provider = BedrockProvider()
    arn = "bedrock/arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0"
    route = provider._route_provider(arn)  # pyright: ignore[reportPrivateUsage]
    assert route is None


def test_bedrock_provider_route_unknown_returns_none() -> None:
    """Test BedrockProvider returns None for unknown model IDs."""
    provider = BedrockProvider()
    route = provider._route_provider("bedrock/amazon.nova-lite-v1:0")  # pyright: ignore[reportPrivateUsage]
    assert route is None


def test_bedrock_provider_routes_unknown_model_to_boto3() -> None:
    """Test BedrockProvider routes unknown models to boto3."""
    provider = BedrockProvider()

    with patch("boto3.Session") as mock_session_cls:
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.client.return_value = mock_client
        mock_session_cls.return_value = mock_session

        mock_client.converse.return_value = {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [{"text": "Hello"}],
                }
            },
            "stopReason": "end_turn",
            "usage": {"inputTokens": 10, "outputTokens": 5},
        }

        response = provider.call(
            model_id="bedrock/amazon.nova-lite-v1:0",
            messages=[user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )
        assert "Hello" in response.pretty()
        mock_client.converse.assert_called_once()


def test_bedrock_provider_missing_anthropic_raises_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test BedrockProvider raises ImportError when Anthropic is unavailable."""
    sys.modules.pop("mirascope.llm.providers.bedrock.anthropic.provider", None)
    sys.modules.pop("mirascope.llm.providers.bedrock.anthropic", None)

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        if name == "anthropic" or name.startswith("anthropic."):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    provider = BedrockProvider()

    with pytest.raises(ImportError, match="anthropic"):
        provider.call(
            model_id="bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0",
            messages=[user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )


def test_bedrock_provider_creates_anthropic_subprovider() -> None:
    """Test BedrockProvider can create the Anthropic subprovider."""
    provider = BedrockProvider(
        aws_region="us-east-1",
    )
    subprovider = provider._get_anthropic_provider()  # pyright: ignore[reportPrivateUsage]
    assert subprovider.id == "bedrock"


def test_bedrock_provider_client_is_set_after_subprovider_creation() -> None:
    """Test BedrockProvider client is set after subprovider is created."""
    provider = BedrockProvider(
        aws_region="us-east-1",
    )
    assert provider.client is None
    provider._get_anthropic_provider()  # pyright: ignore[reportPrivateUsage]
    assert provider.client is not None


def test_bedrock_provider_routing_scopes_extend_defaults() -> None:
    """Test BedrockProvider routing_scopes extend default scopes."""
    provider = BedrockProvider(
        routing_scopes={"anthropic": ["bedrock/my-custom-prefix."]},
    )
    scopes = provider._routing_scopes["anthropic"]  # pyright: ignore[reportPrivateUsage]
    # Should contain both default and custom scopes
    assert "bedrock/anthropic." in scopes
    assert "bedrock/my-custom-prefix." in scopes


def test_bedrock_provider_longest_prefix_match() -> None:
    """Test BedrockProvider selects longest matching prefix."""
    provider = BedrockProvider(
        routing_scopes={"anthropic": ["bedrock/anthropic.claude-3-5-sonnet"]},
    )
    # Both "bedrock/anthropic." and "bedrock/anthropic.claude-3-5-sonnet" match,
    # but the longer one should be selected
    route = provider._route_provider(  # pyright: ignore[reportPrivateUsage]
        "bedrock/anthropic.claude-3-5-sonnet-20241022-v1:0"
    )
    assert route == "anthropic"


def test_bedrock_provider_route_openai_model() -> None:
    """Test BedrockProvider routes OpenAI-compatible model IDs."""
    provider = BedrockProvider()
    route = provider._route_provider(  # pyright: ignore[reportPrivateUsage]
        "bedrock/openai.gpt-4"
    )
    assert route == "openai"


def test_bedrock_provider_default_routing_scopes_has_openai() -> None:
    """Test default routing scopes include OpenAI prefixes."""
    scopes = _default_routing_scopes()
    assert "openai" in scopes
    assert len(scopes["openai"]) > 0


def test_bedrock_provider_initialization_with_anthropic_api_key() -> None:
    """Test BedrockProvider creates API key client for Anthropic subprovider."""
    from mirascope.llm.providers.bedrock.anthropic.provider import (
        BedrockAnthropicApiKeyClient,
    )

    provider = BedrockProvider(
        anthropic_api_key="test-api-key",
        aws_region="us-east-1",
    )
    subprovider = provider._get_anthropic_provider()  # pyright: ignore[reportPrivateUsage]
    assert isinstance(subprovider.client, BedrockAnthropicApiKeyClient)


def test_bedrock_provider_initialization_with_openai_api_key() -> None:
    """Test BedrockProvider creates API key client for OpenAI subprovider."""
    provider = BedrockProvider(
        openai_api_key="test-api-key",
        aws_region="us-east-1",
    )
    subprovider = provider._get_openai_provider()  # pyright: ignore[reportPrivateUsage]
    assert subprovider.client.api_key == "test-api-key"


def test_bedrock_provider_rejects_model_without_bedrock_prefix() -> None:
    """Test BedrockProvider raises ValueError for model IDs without bedrock/ prefix."""
    provider = BedrockProvider()

    with pytest.raises(ValueError, match="bedrock/"):
        provider.call(
            model_id="anthropic.claude-3-5-sonnet-20241022-v1:0",
            messages=[user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )


def test_bedrock_provider_missing_openai_raises_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test BedrockProvider raises ImportError when OpenAI is unavailable for OpenAI models."""
    from mirascope.llm.providers.bedrock.openai.provider import (
        BedrockOpenAIRoutedProvider,
    )

    def mock_init(*args: object, **kwargs: object) -> None:  # noqa: ARG001
        raise ImportError("No module named 'openai'")

    monkeypatch.setattr(BedrockOpenAIRoutedProvider, "__init__", mock_init)

    provider = BedrockProvider()

    with pytest.raises(ImportError, match="openai"):
        provider.call(
            model_id="bedrock/openai.gpt-4",
            messages=[user("hello")],
            toolkit=EMPTY_TOOLKIT,
        )


def test_bedrock_provider_missing_boto3_raises_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test BedrockProvider raises ImportError when boto3 is unavailable for boto3-routed models."""
    # Clear cached modules
    modules_to_remove = [
        "mirascope.llm.providers.bedrock.boto3.provider",
        "mirascope.llm.providers.bedrock.boto3",
    ]
    original_modules = {name: sys.modules.get(name) for name in modules_to_remove}
    for name in modules_to_remove:
        sys.modules.pop(name, None)

    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401
        if name == "boto3" or name.startswith("boto3."):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    try:
        provider = BedrockProvider()

        with pytest.raises(ImportError, match="bedrock"):
            provider.call(
                model_id="bedrock/amazon.nova-lite-v1:0",
                messages=[user("hello")],
                toolkit=EMPTY_TOOLKIT,
            )
    finally:
        # Restore modules
        for name, module in original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def test_bedrock_provider_boto3_fallback_for_unknown_models() -> None:
    """Test BedrockProvider falls back to boto3 for unknown bedrock/ models."""
    provider = BedrockProvider()

    # Verify that _route_provider returns None for unknown models
    route = provider._route_provider("bedrock/some-unknown-model-v1:0")  # pyright: ignore[reportPrivateUsage]
    assert route is None

    # Now verify _choose_subprovider falls back to boto3
    with patch("boto3.Session") as mock_session_cls:
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.client.return_value = mock_client
        mock_session_cls.return_value = mock_session

        subprovider = provider._choose_subprovider(  # pyright: ignore[reportPrivateUsage]
            "bedrock/some-unknown-model-v1:0", [user("hello")]
        )
        assert subprovider.id == "bedrock"  # BedrockBoto3RoutedProvider


def test_bedrock_provider_explicit_boto3_routing() -> None:
    """Test BedrockProvider routes to boto3 when explicitly specified in routing scopes."""
    # Create provider with explicit boto3 routing scope
    provider = BedrockProvider(
        routing_scopes={"boto3": ["bedrock/custom-boto3-model."]},
    )

    # Verify that _route_provider returns "boto3" for custom prefix
    route = provider._route_provider("bedrock/custom-boto3-model.test-v1:0")  # pyright: ignore[reportPrivateUsage]
    assert route == "boto3"

    # Now verify _choose_subprovider returns boto3 provider
    with patch("boto3.Session") as mock_session_cls:
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_session.client.return_value = mock_client
        mock_session_cls.return_value = mock_session

        subprovider = provider._choose_subprovider(  # pyright: ignore[reportPrivateUsage]
            "bedrock/custom-boto3-model.test-v1:0", [user("hello")]
        )
        assert subprovider.id == "bedrock"  # BedrockBoto3RoutedProvider


def test_resolve_region_with_aws_profile_botocore_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test resolve_region uses botocore session when aws_profile is provided."""
    from mirascope.llm.providers.bedrock._utils import resolve_region

    # Clear environment variables
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)

    # Mock botocore session
    class MockSession:
        def __init__(self, profile: str | None = None) -> None:
            self.profile = profile

        def get_config_variable(
            self, logical_name: str, methods: object | None = None
        ) -> str | None:
            if logical_name == "region":
                return "eu-west-1"
            return None

    # Patch botocore.session.Session
    import mirascope.llm.providers.bedrock._utils as utils_module

    monkeypatch.setattr(
        utils_module,
        "Session",
        MockSession,
        raising=False,
    )

    # Need to patch the import inside the function
    import botocore.session

    monkeypatch.setattr(botocore.session, "Session", MockSession)

    region = resolve_region(None, aws_profile="my-profile")
    assert region == "eu-west-1"


def test_resolve_region_with_aws_profile_botocore_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test resolve_region falls back to default when botocore import fails."""
    from mirascope.llm.providers.bedrock._utils import DEFAULT_REGION, resolve_region

    # Clear environment variables
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)

    # Mock the import to raise ImportError
    import builtins

    original_import = builtins.__import__

    def mock_import(
        name: str,
        *args: object,
        **kwargs: object,  # noqa: ANN002, ANN003
    ) -> ModuleType:
        if name == "botocore.session" or name.startswith("botocore"):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", mock_import)

    # Force re-evaluation of the import inside the function
    region = resolve_region(None, aws_profile="my-profile")
    assert region == DEFAULT_REGION


def test_resolve_region_with_aws_profile_returns_none_region(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test resolve_region falls back to default when profile has no region."""
    from mirascope.llm.providers.bedrock._utils import DEFAULT_REGION, resolve_region

    # Clear environment variables
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)

    # Mock botocore session that returns None for region
    class MockSession:
        def __init__(self, profile: str | None = None) -> None:
            self.profile = profile

        def get_config_variable(
            self, logical_name: str, methods: object | None = None
        ) -> str | None:
            return None

    import botocore.session

    monkeypatch.setattr(botocore.session, "Session", MockSession)

    region = resolve_region(None, aws_profile="my-profile")
    assert region == DEFAULT_REGION
