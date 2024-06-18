"""Types for the Mirascope OpenAI module."""

from __future__ import annotations

from typing import Any

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import ChatCompletionMessage, Choice
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.completion_usage import CompletionUsage
from typing_extensions import TypedDict

from ..base.tool import BaseTool
from ..base.types import BaseCallResponse


class OpenAITool(BaseTool):
    """A class for defining tools for OpenAI LLM calls."""


class OpenAICallParams(TypedDict):
    """The parameters to use when calling the OpenAI API."""

    model: str = "gpt-4o-2024-05-13"
    frequency_penalty: float | None = None
    logit_bias: dict[str, int] | None = None
    logprobs: bool | None = None
    max_tokens: int | None = None
    n: int | None = None
    presence_penalty: float | None = None
    response_format: ResponseFormat | None = None
    seed: int | None = None
    stop: str | list[str] | None = None
    temperature: float | None = None
    # tools: list[BaseTool] | None = None
    tool_choice: ChatCompletionToolChoiceOptionParam | None = None
    top_logprobs: int | None = None
    top_p: float | None = None
    user: str | None = None


class OpenAICallResponse(
    BaseCallResponse[ChatCompletion, ChatCompletionUserMessageParam]
):
    '''A convenience wrapper around the OpenAI `ChatCompletion` response.

    When calling the OpenAI API using a function decorated with `openai_call`, the
    response will be an `OpenAICallResponse` instance with properties that allow for
    more convenience access to commonly used attributes.

    Example:

    ```python
    from mirascope.core.openai import openai_call

    @openai_call(model="gpt-4o")
    def recommend_book(genre: str):
        """Recommend a {genre} book."""

    response = recommend_book("fantasy")  # response is an `OpenAICallResponse` instance
    print(response.content)
    #> Sure! I would recommend...
    ```
    '''

    response_format: ResponseFormat | None = None

    @property
    def message_param(self) -> ChatCompletionAssistantMessageParam:
        """Returns the assistants's response as a message parameter."""
        return self.message.model_dump(exclude={"function_call"})  # type: ignore

    @property
    def choices(self) -> list[Choice]:
        """Returns the array of chat completion choices."""
        return self.response.choices

    @property
    def choice(self) -> Choice:
        """Returns the 0th choice."""
        return self.choices[0]

    @property
    def message(self) -> ChatCompletionMessage:
        """Returns the message of the chat completion for the 0th choice."""
        return self.choice.message

    @property
    def content(self) -> str:
        """Returns the content of the chat completion for the 0th choice."""
        return self.message.content if self.message.content is not None else ""

    @property
    def model(self) -> str:
        """Returns the name of the response model."""
        return self.response.model

    @property
    def id(self) -> str:
        """Returns the id of the response."""
        return self.response.id

    @property
    def finish_reasons(self) -> list[str]:
        """Returns the finish reasons of the response."""
        return [str(choice.finish_reason) for choice in self.response.choices]

    @property
    def tool_calls(self) -> list[ChatCompletionMessageToolCall] | None:
        """Returns the tool calls for the 0th choice message."""
        return self.message.tool_calls

    #     @property
    #     def tools(self) -> Optional[list[OpenAITool]]:
    #         """Returns the tools for the 0th choice message.

    #         Raises:
    #             ValidationError: if a tool call doesn't match the tool's schema.
    #         """
    #         if not self.tool_types:
    #             return None

    #         if self.choice.finish_reason == "length":
    #             raise RuntimeError(
    #                 "Finish reason was `length`, indicating the model ran out of tokens "
    #                 "(and could not complete the tool call if trying to)"
    #             )

    #         def reconstruct_tools_from_content() -> list[OpenAITool]:
    #             # Note: we only handle single tool calls in this case
    #             tool_type = self.tool_types[0]  # type: ignore
    #             return [
    #                 tool_type.from_tool_call(
    #                     ChatCompletionMessageToolCall(
    #                         id="id",
    #                         function=Function(
    #                             name=tool_type.name(), arguments=self.content
    #                         ),
    #                         type="function",
    #                     )
    #                 )
    #             ]

    #         if self.response_format == ResponseFormat(type="json_object"):
    #             return reconstruct_tools_from_content()

    #         if not self.tool_calls:
    #             # Let's see if we got an assistant message back instead and try to
    #             # reconstruct a tool call in this case. We'll assume if it starts with
    #             # an open curly bracket that we got a tool call assistant message.
    #             if "{" == self.content[0]:
    #                 # Note: we only handle single tool calls in JSON mode.
    #                 return reconstruct_tools_from_content()
    #             return None

    #         extracted_tools = []
    #         for tool_call in self.tool_calls:
    #             for tool_type in self.tool_types:
    #                 if tool_call.function.name == tool_type.name():
    #                     extracted_tools.append(tool_type.from_tool_call(tool_call))
    #                     break

    #         return extracted_tools

    #     @property
    #     def tool(self) -> Optional[OpenAITool]:
    #         """Returns the 0th tool for the 0th choice message.

    #         Raises:
    #             ValidationError: if the tool call doesn't match the tool's schema.
    #         """
    #         tools = self.tools
    #         if tools:
    #             return tools[0]
    #         return None

    #     @classmethod
    #     def tool_message_params(
    #         self, tools_and_outputs: list[tuple[OpenAITool, str]]
    #     ) -> list[ChatCompletionToolMessageParam]:
    #         return [
    #             ChatCompletionToolMessageParam(
    #                 role="tool",
    #                 content=output,
    #                 tool_call_id=tool.tool_call.id,
    #                 name=tool.name(),  # type: ignore
    #             )
    #             for tool, output in tools_and_outputs
    #         ]

    @property
    def usage(self) -> CompletionUsage | None:
        """Returns the usage of the chat completion."""
        return self.response.usage

    @property
    def input_tokens(self) -> int | None:
        """Returns the number of input tokens."""
        return self.usage.prompt_tokens if self.usage else None

    @property
    def output_tokens(self) -> int | None:
        """Returns the number of output tokens."""
        return self.usage.completion_tokens if self.usage else None

    def dump(self) -> dict[str, Any]:
        """Dumps the response to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "output": self.response.model_dump(),
            "cost": self.cost,
        }
