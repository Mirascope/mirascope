"""Utility functions for Mistral convenience wrapper."""
from typing import Any, Optional, Type

from ..base.prompt import BasePrompt
from .tools import MistralTool


def patch_mistral_kwargs(
    kwargs: dict[str, Any],
    prompt: BasePrompt,
    tools: Optional[list[Type[MistralTool]]],
) -> None:
    """Sets up the kwargs for a Mistral API call.

    Kwargs are parsed as such: messages are formatted to have the required `role` and
    `content` items; tools (if any exist) are parsed into JSON schemas in order to fit
    the OpenAI API; tool choice, if not provided, is set to "auto". Other kwargs are
    left unchanged.

    Args:
        kwargs: The kwargs to patch.
        prompt: The prompt to use.
        tools: The tools to use, if any.

    """
    kwargs["messages"] = prompt.messages
    kwargs.update(
        {
            key: value
            for key, value in prompt.call_params.model_dump(
                exclude={"tools", "model", "wrapper", "async_wrapper", "endpoint"}
            ).items()
            if value is not None
        }
    )

    if tools:
        # TODO
        pass
