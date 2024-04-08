"""A module for convenience around streaming tools with OpenAI."""
# from typing import Any, Generator

# from ..base.tool_stream import BaseToolStream


# class OpenAIToolStream(BaseToolStream):
#     """A base class for streaming tools from response chunks."""

#     @classmethod
#     def stream(self, stream: Any) -> Generator[str, None, None]:
#         for i in range(5):
#             yield "OpenAI" + str(i)


# from typing import (
#     Any,
#     AsyncGenerator,
#     Generator,
#     Literal,
#     Optional,
#     TypeVar,
#     Union,
#     overload,
# )

# from openai.types.chat.chat_completion_message_tool_call import (
#     ChatCompletionMessageToolCall,
#     Function,
# )

# from ..base.tool_stream import BaseToolStream
# from ..partial import Partial
# from .tools import OpenAITool
# from .types import OpenAICallResponseChunk

# T = TypeVar("T", bound=Union[OpenAITool, Optional[Partial[OpenAITool]]])


# class OpenAIToolStream(BaseToolStream[OpenAITool]):
#     """A base class for streaming tools from response chunks."""

#     # @classmethod
#     # @overload
#     # def from_stream(
#     #     self,
#     #     stream: Generator[OpenAICallResponseChunk, None, None],
#     #     partial: Literal[True],
#     # ) -> Generator[Optional[Partial[OpenAITool]], None, None]:
#     #     ...  # pragma: no cover

#     # @classmethod
#     # @overload
#     # def from_stream(
#     #     self,
#     #     stream: Generator[OpenAICallResponseChunk, None, None],
#     #     partial: Literal[False],
#     # ) -> Generator[OpenAITool, None, None]:
#     #     ...  # pragma: no cover

#     @classmethod
#     def from_stream(
#         self,
#         stream,
#         partial: bool = False,
#     ):
#         """Yields partial tools from the given stream of chunks.

#         Raises:
#             RuntimeError: if a tool in the stream is of an unknown type.
#         """
#         current_tool_type = None
#         current_tool_call = ChatCompletionMessageToolCall(
#             id="", function=Function(arguments="", name=""), type="function"
#         )
#         for chunk in stream:
#             if not chunk.tool_calls:
#                 continue
#             tool_call = chunk.tool_calls[0]
#             # Reset on new tool
#             if tool_call.id:
#                 previous_tool_call = current_tool_call.model_copy()
#                 current_tool_call = ChatCompletionMessageToolCall(
#                     id=tool_call.id,
#                     function=Function(arguments="", name=tool_call.function.name),
#                     type="function",
#                 )
#                 current_tool_type = None
#                 for tool_type in chunk.tool_types:
#                     if tool_type.__name__ == tool_call.function.name:
#                         current_tool_type = tool_type
#                         break
#                 if current_tool_type is None:
#                     raise RuntimeError(
#                         f"Unknown tool type in stream: {tool_call.function.name}"
#                     )
#                 if previous_tool_call.id:
#                     yield current_tool_type.from_tool_call(previous_tool_call)

#             # Update arguments with each chunk
#             if tool_call.function:
#                 current_tool_call.function.arguments += tool_call.function.arguments

#             if partial:
#                 yield Partial[current_tool_type].from_tool_call(current_tool_call)

#     @classmethod
#     async def from_async_stream(
#         # self, async_stream: AsyncGenerator[OpenAICallResponseChunk, None]
#         self,
#         async_stream: Any,
#     ) -> AsyncGenerator[Partial[OpenAITool], None]:
#         """Yields partial tools asynchronously from the given async stream of chunks."""
#         ...  # pragma: no cover
