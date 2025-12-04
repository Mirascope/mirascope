"""Tests for the context utilities."""

from mirascope import llm
from mirascope.llm.context._utils import first_param_is_context


def test_context_parameter_name_independence() -> None:
    """Test that context prompts require the first parameter be named ctx."""

    def context_weird_name(special_context: llm.Context[str]) -> str:
        return f"Value: {special_context.deps}"

    assert not first_param_is_context(context_weird_name)


def test_non_context_typed_parameter() -> None:
    """Test that non-Context typed parameters are not treated as context prompts."""

    def non_context_prompt(ctx: int) -> str:
        return f"Value: {ctx}"

    assert not first_param_is_context(non_context_prompt)


def test_missing_type_annotation() -> None:
    """Test that missing type annotations are not treated as context prompts."""

    def missing_annotation_prompt(ctx) -> str:  # pyright: ignore[reportMissingParameterType] # noqa: ANN001
        return "hi"

    assert not first_param_is_context(missing_annotation_prompt)


def test_method_with_context_after_self() -> None:
    """Test that methods with self as first arg and Context as second arg are context prompts."""

    class TestClass:
        def method_with_context(self, ctx: llm.Context[str]) -> str:
            return f"Value: {ctx.deps}"

    assert first_param_is_context(TestClass.method_with_context)


def test_context_not_first_parameter() -> None:
    """Test that Context as second parameter (after non-self) is not treated as context prompt."""

    def second_arg_context(regular_param: int, ctx: llm.Context[str]) -> str:
        return f"Value: {regular_param}-{ctx.deps}"

    assert not first_param_is_context(second_arg_context)


def test_context_subclass_detection() -> None:
    """Test that Context subclasses are properly detected as context prompts."""

    class CustomContext(llm.Context[str]): ...

    def with_custom_context(ctx: CustomContext) -> str:
        return str(ctx.deps)

    assert first_param_is_context(with_custom_context)


def test_context_first_parameter_with_correct_name() -> None:
    """Test that Context as first parameter with name 'ctx' is detected."""

    def valid_context_prompt(ctx: llm.Context[str]) -> str:
        return f"Value: {ctx.deps}"

    assert first_param_is_context(valid_context_prompt)


def test_classmethod_with_context_after_cls() -> None:
    """Test that classmethods with cls as first arg and Context as second arg are context prompts."""

    class TestClass:
        @classmethod
        def method_with_context(cls, ctx: llm.Context[str]) -> str:
            return f"Value: {ctx.deps}"

    assert first_param_is_context(TestClass.method_with_context)


def test_no_parameters() -> None:
    """Test that functions with no parameters return False."""

    def no_params() -> str:
        return "hi"

    assert not first_param_is_context(no_params)


def test_forward_reference_context() -> None:
    """Test that forward references to Context are handled via the except path."""

    def with_forward_ref(ctx: "llm.Context[str]") -> str:  # noqa: F821
        return "hi"

    # Should hit the except block but still work via first_param.annotation
    assert first_param_is_context(with_forward_ref)


def test_undefined_forward_reference() -> None:
    """Test that undefined forward references fall back to first_param.annotation."""

    def with_undefined_forward_ref(ctx: "UndefinedType") -> str:  # pyright: ignore[reportUndefinedVariable] # noqa: F821
        return "hi"

    # Should hit the except block and return False since it's not a Context type
    assert not first_param_is_context(with_undefined_forward_ref)
