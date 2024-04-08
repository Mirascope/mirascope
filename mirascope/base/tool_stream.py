"""A base module for convenience around streaming tools."""
# from typing import Any, Generator

# from pydantic import BaseModel


# class BaseToolStream(BaseModel):
#     """A base class for streaming tools from response chunks."""

#     @classmethod
#     def from_stream(self, stream: Any) -> Generator[str, None, None]:
#         for i in range(5):
#             return str(i)


# from abc import ABC, abstractmethod
# from typing import Any, AsyncGenerator, Generator

# import pydantic
# from pydantic import BaseModel

# from .tools import BaseTool

# # from .types import BaseCallResponseChunk

# if int(pydantic.__version__.split(".")[1]) < 7:
#     raise ImportError(
#         "You must have `pydantic==^2.7.0` to stream tools. "
#         f"Current version: {pydantic.__version__}"
#     )


# class BaseToolStream(BaseModel, ABC):
#     """A base class for streaming tools from response chunks."""

#     @classmethod
#     @abstractmethod
#     def from_stream(
#         # self, stream: Generator[BaseCallResponseChunkT, None, None]
#         self,
#         stream: Any,
#     ) -> Generator[BaseTool, None, None]:
#         """Yields partial tools from the given stream of chunks."""
#         ...  # pragma: no cover

#     @classmethod
#     @abstractmethod
#     async def from_async_stream(
#         # self, async_stream: AsyncGenerator[BaseCallResponseChunkT, None]
#         self,
#         async_stream: Any,
#     ) -> AsyncGenerator[BaseTool, None]:
#         """Yields partial tools asynchronously from the given async stream of chunks."""
#         ...  # pragma: no cover
