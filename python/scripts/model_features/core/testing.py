"""Feature test protocol and base implementations."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from .models import FeatureTestResult

# Generic type for the client
ClientT = TypeVar("ClientT")


class FeatureTest(ABC, Generic[ClientT]):
    """Abstract base class for feature tests.

    To create a new feature test:
    1. Subclass FeatureTest with your client type
    2. Set the `name` class attribute
    3. Implement the `test` method

    Example:
        from openai import OpenAI

        class ReasoningSupport(FeatureTest[OpenAI]):
            name = "reasoning"

            def test(self, model_id: str, client: OpenAI) -> FeatureTestResult:
                try:
                    client.responses.create(
                        model=model_id,
                        input=[{"role": "user", "content": "Say hello"}],
                        reasoning={"effort": "medium"},
                    )
                    return FeatureTestResult(status=TestStatus.SUPPORTED)
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        return FeatureTestResult(
                            status=TestStatus.UNAVAILABLE,
                            error_message=str(e)
                        )
                    if "unsupported parameter" in str(e).lower():
                        return FeatureTestResult(status=TestStatus.NOT_SUPPORTED)
                    return FeatureTestResult(
                        status=TestStatus.ERROR,
                        error_message=str(e)
                    )
    """

    name: str  # Must be set by subclasses
    dependencies: list[str] = []  # Optional list of feature names this test depends on

    def __init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "name", None) and not getattr(
            cls, "__abstractmethods__", None
        ):
            raise TypeError(f"{cls.__name__} must define a 'name' class attribute")

    @abstractmethod
    def test(self, model_id: str, client: ClientT) -> FeatureTestResult:
        """Test whether a model supports this feature.

        Args:
            model_id: The model identifier to test
            client: The provider client (e.g., OpenAI client)

        Returns:
            FeatureTestResult with the test outcome
        """
        ...

    def __repr__(self) -> str:
        return f"<FeatureTest: {self.name}>"
