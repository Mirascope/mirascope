"""A module for prompting Mistral API."""
import datetime
import os
import re
from typing import Annotated, Any, ClassVar, Optional

from mistralai.client import MistralClient
from pydantic import AfterValidator

from ..base.prompt import BasePrompt, format_template
from ..base.types import (
    AssistantMessage,
    Message,
    SystemMessage,
    UserMessage,
)
from .types import MistralCallParams, MistralChatCompletion
from .utils import patch_mistral_kwargs


def _set_api_key(api_key: str) -> None:
    """Sets the MISTRAL_API_KEY environment variable."""
    os.environ["MISTRAL_API_KEY"] = api_key
    return None


class MistralPrompt(BasePrompt):
    """A class for" prompting Mistral's chat API.

    Example:

    TODO:
    ```python
    import mistralai
    ```
    """

    api_key: Annotated[
        Optional[str],
        AfterValidator(lambda key: _set_api_key(key) if key is not None else None),
    ] = None

    call_params: ClassVar[MistralCallParams] = MistralCallParams(
        model="open-mixtral-8x7b",
    )

    @property
    def messages(self) -> list[Message]:
        """Returns the docstring as a list of messages.

        Raises:
            ValueError: if docstring contains an unknown role.
        """
        message_param_map = {
            "system": SystemMessage,
            "user": UserMessage,
            "assistant": AssistantMessage,
        }
        messages = []
        for match in re.finditer(
            r"(SYSTEM|USER|ASSISTANT|[A-Z]*): "
            r"((.|\n)+?)(?=\n(SYSTEM|USER|ASSISTANT|[A-Z]*):|\Z)",
            self.template(),
        ):
            role = match.group(1).lower()
            if role not in ["system", "user", "assistant"]:
                raise ValueError(f"Unknown role: {role}")
            content = format_template(self, match.group(2))
            messages.append(message_param_map[role](role=role, content=content))
        if len(messages) == 0:
            messages.append(UserMessage(role="user", content=str(self)))
        return messages

    def create(self, **kwargs: Any) -> MistralChatCompletion:
        if self.call_params.endpoint:
            client = MistralClient(endpoint=self.call_params.endpoint)
        else:
            client = MistralClient()

        # TODO: tools logic
        patch_mistral_kwargs(
            kwargs,
            prompt=self,
            tools=self.call_params.tools,
        )
        completion_start_time = datetime.datetime.now().timestamp() * 1000
        completion = client.chat(model=self.call_params.model, **kwargs)
        return MistralChatCompletion(
            completion=completion,
            tool_types=self.call_params.tools,
            start_time=completion_start_time,
            end_time=datetime.datetime.now().timestamp() * 1000,
        )
