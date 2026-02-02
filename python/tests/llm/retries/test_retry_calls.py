"""Tests for RetryCall model override behavior."""

from mirascope import llm


def _create_retry_call(retry_config: llm.RetryConfig) -> llm.RetryCall[..., None]:
    """Helper to create a RetryCall for testing."""

    def my_prompt() -> str:
        return "test"

    prompt = llm.RetryPrompt(
        fn=my_prompt,
        toolkit=llm.tools.Toolkit(tools=None),
        format=None,
        retry_config=retry_config,
    )
    return llm.RetryCall(
        default_model=llm.Model("openai/gpt-4o"),
        prompt=prompt,
    )


class TestRetryCallModelOverride:
    """Tests for how RetryCall handles model overrides via context."""

    def test_retry_call_wraps_default_model_in_retry_model(self) -> None:
        """Test that RetryCall.model wraps the default model in RetryModel."""
        retry_call = _create_retry_call(llm.RetryConfig(max_retries=3))

        model = retry_call.model

        assert isinstance(model, llm.RetryModel)
        assert model.model_id == "openai/gpt-4o"
        assert model.retry_config.max_retries == 3

    def test_retry_call_wraps_context_model_in_retry_model(self) -> None:
        """Test that RetryCall.model wraps context override in RetryModel."""
        retry_call = _create_retry_call(llm.RetryConfig(max_retries=3))

        with llm.model("anthropic/claude-sonnet-4-0"):
            model = retry_call.model

            assert isinstance(model, llm.RetryModel)
            assert model.model_id == "anthropic/claude-sonnet-4-0"
            # Uses the prompt's retry config when wrapping
            assert model.retry_config.max_retries == 3

    def test_retry_call_uses_override_retry_model_directly(self) -> None:
        """Test that if context override is a RetryModel, it's used as-is."""
        retry_call = _create_retry_call(llm.RetryConfig(max_retries=3))

        override_retry_model = llm.RetryModel(
            "anthropic/claude-sonnet-4-0",
            llm.RetryConfig(max_retries=5),
        )

        with override_retry_model:
            model = retry_call.model

            assert isinstance(model, llm.RetryModel)
            assert model.model_id == "anthropic/claude-sonnet-4-0"
            # The override's retry config should win, not the prompt's
            assert model.retry_config.max_retries == 5

    def test_retry_call_override_retry_model_is_same_instance(self) -> None:
        """Test that the override RetryModel is returned directly, not re-wrapped."""
        retry_call = _create_retry_call(llm.RetryConfig(max_retries=3))

        override_retry_model = llm.RetryModel(
            "anthropic/claude-sonnet-4-0",
            llm.RetryConfig(max_retries=5),
        )

        with override_retry_model:
            model = retry_call.model
            # Should be the exact same instance, not wrapped
            assert model is override_retry_model

    def test_retry_config_property_returns_prompt_config(self) -> None:
        """Test that retry_config property returns the prompt's retry config."""
        config = llm.RetryConfig(max_retries=7)
        retry_call = _create_retry_call(config)

        assert retry_call.retry_config is config
        assert retry_call.retry_config.max_retries == 7
