from __future__ import annotations

import asyncio
import base64
import inspect
import json
import os
from collections import defaultdict
from collections.abc import Callable
from functools import lru_cache
from io import BytesIO
from typing import (
    Any,
    Literal,
    TypeAlias,
    TypedDict,
    TypeVar,
)

import websockets
from pydantic import BaseModel
from pydub import AudioSegment
from typing_extensions import NotRequired, overload
from websockets.asyncio.client import ClientConnection, connect

from ....core import BaseTool
from ....core.base._utils import (
    convert_base_model_to_base_tool,
    convert_function_to_base_tool,
)
from ._utils._audio import (
    async_audio_input_audio_buffer_append_event,
    async_audio_to_item_create_event,
    audio_chunk_to_audio_segment,
)
from ._utils._protocols import FunctionCallHandlerFunc, ReceiverFunc, SenderFunc
from .tool import FunctionCallArguments, OpenAIRealtimeTool, RealtimeToolParam

ChunkResponseType: TypeAlias = Literal[
    "text_chunk",
    "audio_chunk",
    "audio_transcript_chunk",
    "tool_chunk",
]
TextResponseType: TypeAlias = Literal[
    "text",
    "audio_transcript",
]
AudioResponseType: TypeAlias = Literal["audio"]
ResponseType: TypeAlias = ChunkResponseType | TextResponseType | AudioResponseType


_ResponseT = TypeVar("_ResponseT")
_ConnectionT = TypeVar("_ConnectionT")
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ToolSchemaT = TypeVar("_ToolSchemaT")

# TODO: Improve the type of response
Response: TypeAlias = Any
ToolName: TypeAlias = str
CallId: TypeAlias = str
ResponseId: TypeAlias = str
ToolType: TypeAlias = type[OpenAIRealtimeTool]


class RawMessage(TypedDict, total=False):
    event_id: str
    type: str
    item: NotRequired[dict]
    delta: NotRequired[str]
    response_id: NotRequired[str]
    tool_name: NotRequired[str]
    response: NotRequired[dict]
    name: NotRequired[str]
    call_id: NotRequired[str]


class Sender(TypedDict):
    func: SenderFunc[_ResponseT, OpenAIRealtimeTool]
    wait_for_text_response: bool
    wait_for_audio_transcript_response: bool
    tools: list[type[BaseModel] | Callable]


class FunctionCallHandler(TypedDict):
    tool_name: ToolName
    func: FunctionCallHandlerFunc


NotSet = object()


@lru_cache
def _convert_to_base_tool(tool: type[BaseModel] | Callable) -> type[ToolType]:
    if inspect.isclass(tool):
        convert_base_model_to_base_tool(tool, OpenAIRealtimeTool)
    return convert_function_to_base_tool(tool, OpenAIRealtimeTool)


def _get_tool_type_and_tool_schemas(
    tools: list[type[BaseModel] | Callable],
) -> dict[ToolName, tuple[ToolType, RealtimeToolParam]]:
    return {
        _tool_type._name(): (_tool_type, _tool_type.tool_schema())
        for tool in tools
        if (_tool_type := _convert_to_base_tool(tool))
    }


class Realtime:
    def __init__(
        self,
        model: str,
        *,
        context: dict[str, Any] | None = None,
        modalities: list[str] | NotSet = NotSet,
        instructions: str | NotSet = NotSet,
        voice: str | NotSet = NotSet,
        turn_detection: dict[str, Any] | None | NotSet = NotSet,
        input_audio_format: str | NotSet = NotSet,
        output_audio_format: str | NotSet = NotSet,
        input_audio_transcription: str | NotSet = NotSet,
        tool_choice: str | NotSet = NotSet,
        temperature: float | NotSet = NotSet,
        max_response_output_tokens: int | float | Literal["inf"] = NotSet,
        tools: list[type[BaseModel] | Callable] | NotSet = NotSet,
    ) -> None:
        self.senders: list[Sender] = []
        self.receivers: defaultdict[ResponseType, ReceiverFunc] = defaultdict(list)
        self.function_call_handlers: dict[ToolName, FunctionCallHandlerFunc] = {}
        self._connection: connect | None = None
        self.context = context or {}
        self._tool_schemas: dict[ToolName, tuple[ToolType, RealtimeToolParam]] = (
            _get_tool_type_and_tool_schemas(tools) if tools is not NotSet else {}
        )
        self._temporary_tool_schemas: defaultdict[
            ToolName, list[tuple[ToolType, RealtimeToolParam]]
        ] = defaultdict(list)
        self._session: dict[str, Any] = {
            "model": model,
            "modalities": modalities,
            "instructions": instructions,
            "voice": voice,
            "turn_detection": turn_detection,
            "input_audio_format": input_audio_format,
            "output_audio_format": output_audio_format,
            "input_audio_transcription": input_audio_transcription,
            "tool_choice": tool_choice,
            "temperature": temperature,
            "max_response_output_tokens": max_response_output_tokens,
            "tools": [tool_schema for _, tool_schema in self._tool_schemas.values()]
            if self._tool_schemas
            else NotSet,
        }
        self._text_message_received: bool = True
        self._audio_transcript_received: bool = True

    async def _wait_for_text_message(self) -> None:
        while not self._text_message_received:
            await asyncio.sleep(0.1)

    async def _wait_for_audio_transcript(self) -> None:
        while not self._audio_transcript_received:
            await asyncio.sleep(0.1)

    def sender(
        self,
        wait_for_text_response: bool = False,
        wait_for_audio_transcript_response: bool = False,
        tools: list[type[BaseModel] | Callable] | None = None,
    ) -> Callable[
        [SenderFunc[_ResponseT, OpenAIRealtimeTool]],
        SenderFunc[_ResponseT, OpenAIRealtimeTool],
    ]:
        def inner(
            func: SenderFunc[_ResponseT, OpenAIRealtimeTool],
        ) -> SenderFunc[_ResponseT, OpenAIRealtimeTool]:
            self.senders.append(
                {
                    "func": func,
                    "wait_for_text_response": wait_for_text_response,
                    "wait_for_audio_transcript_response": wait_for_audio_transcript_response,
                    "tools": tools,
                }
            )
            return func

        return inner

    @overload
    def receiver(
        self, response_type: ChunkResponseType
    ) -> Callable[[ReceiverFunc[dict[str, Any]]], ReceiverFunc[dict[str, Any]]]: ...

    @overload
    def receiver(
        self, response_type: TextResponseType
    ) -> Callable[[ReceiverFunc[str]], ReceiverFunc[str]]: ...
    @overload
    def receiver(
        self, response_type: AudioResponseType
    ) -> Callable[[ReceiverFunc[AudioSegment]], ReceiverFunc[AudioSegment]]: ...

    def receiver(
        self, response_type: ResponseType
    ) -> Callable[[ReceiverFunc[_ResponseT]], ReceiverFunc[_ResponseT]]:
        def inner(func: ReceiverFunc[_ResponseT]) -> ReceiverFunc[_ResponseT]:
            self.receivers[response_type].append(func)
            return func

        return inner

    def function_call(
        self, tool: type[BaseModel] | Callable
    ) -> Callable[[FunctionCallHandlerFunc], FunctionCallHandlerFunc]:
        def inner(func: FunctionCallHandlerFunc) -> FunctionCallHandlerFunc:
            base_tool = _convert_to_base_tool(tool)
            self.function_call_handlers[base_tool._name()] = func
            return func

        return inner

    async def _create_response(
        self,
        conn: ClientConnection,
        tools: list[type[BaseModel] | Callable] | None = None,
    ) -> None:
        if tools is not None:
            tool_schemas = _get_tool_type_and_tool_schemas(tools)
            schemas = []
            for tool_name, tool_type_and_tool_schema in tool_schemas.items():
                self._temporary_tool_schemas[tool_name].append(
                    tool_type_and_tool_schema
                )
                schemas.append(tool_type_and_tool_schema[1])
            event = {"type": "response.create", "response": {"tools": schemas}}
        else:
            event = {"type": "response.create"}
        await self._send_event(conn, event)

    async def _create_audio_input_buffer_commit(self, conn: ClientConnection) -> None:
        await self._send_event(conn, {"type": "input_audio_buffer.commit"})

    async def _create_conversation_item_create(
        self, conn: ClientConnection, message: str
    ) -> None:
        await self._send_event(
            conn,
            {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": message}],
                },
            },
        )

    async def _create_session_update(
        self,
        conn: ClientConnection,
        tools: list[type[BaseModel] | Callable] | None = None,
    ) -> None:
        await self._send_event(
            conn,
            {
                "type": "session.update",
                "session": {
                    **self._session,
                    "tools": [
                        tool_schema
                        for _, tool_schema in _get_tool_type_and_tool_schemas(
                            tools
                        ).values()
                    ],
                }
                if tools
                else self._session,
            },
        )

    @classmethod
    async def _send_event(cls, conn: ClientConnection, event: dict[str, Any]) -> None:
        await conn.send(json.dumps(event))

    async def _wait_for_responses(self, sender: Sender) -> None:
        if sender["wait_for_text_response"]:
            await self._wait_for_text_message()
        if sender["wait_for_audio_transcript_response"]:
            await self._wait_for_audio_transcript()

    def _set_wait_for_flags(self, sender: Sender) -> None:
        if sender["wait_for_audio_transcript_response"]:
            self._audio_transcript_received = False
        if sender["wait_for_text_response"]:
            self._text_message_received = False

    async def _sender_process_loop(
        self, conn: ClientConnection, sender: Sender
    ) -> None:
        while True:
            await self._wait_for_responses(sender)
            if inspect.isasyncgenfunction(sender["func"]):
                input_audio_buffer: bool = False
                if tools := sender.get("tools"):
                    await self._create_session_update(conn, tools)
                async for message in sender["func"](self.context):
                    if isinstance(message, tuple):
                        message, tools = message
                        if tools:
                            await self._create_conversation_item_create(conn, message)
                    match message:
                        case BytesIO() | bytes():
                            event = await async_audio_input_audio_buffer_append_event(
                                message
                            )
                            await self._send_event(conn, event)
                            input_audio_buffer = True
                        case str():
                            await self._create_conversation_item_create(conn, message)
                        case _:
                            continue
                if input_audio_buffer:
                    await self._create_audio_input_buffer_commit(conn)
                await self._create_response(conn)
            else:
                tools = None
                message = await sender["func"](self.context)

                if isinstance(message, tuple):
                    message, tools = message
                    await self._create_conversation_item_create(conn, message)
                    await self._create_response(conn, tools)
                match message:
                    case BytesIO() | bytes():
                        event = await async_audio_to_item_create_event(message)
                        await self._send_event(conn, event)
                    case str():
                        await self._create_conversation_item_create(conn, message)
                    case _:
                        continue
                await self._create_response(conn, tools or sender.get("tools"))
            self._set_wait_for_flags(sender)

    async def _process_sender(self, conn: ClientConnection) -> None:
        try:
            tasks = (
                asyncio.create_task(self._sender_process_loop(conn, s))
                for s in self.senders
            )
            await asyncio.gather(*tasks)
        finally:
            await conn.close()

    async def _process_specific_function_call_handler(
        self,
        conn: ClientConnection,
        call_id: CallId,
        tool_name: ToolName,
        tool: OpenAIRealtimeTool,
    ) -> None:
        function_call_handler = self.function_call_handlers[tool_name]
        function_call_output = await function_call_handler(tool, self.context)
        await self._send_event(
            conn,
            {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": function_call_output,
                },
            },
        )
        await self._send_event(conn, {"type": "response.create"})

    async def _process_specific_receiver(
        self,
        message: dict[str, Any] | str | AudioSegment | OpenAIRealtimeTool,
        response_type: ResponseType,
    ) -> None:
        for receiver in self.receivers[response_type]:
            await receiver(message, self.context)

    async def _process_receiver(self, conn: ClientConnection) -> None:
        try:
            audio_chunks: defaultdict[ResponseId, bytes] = defaultdict(bytes)
            text_chunks: defaultdict[ResponseId, str] = defaultdict(str)
            audio_transcript_chunks: defaultdict[ResponseId, str] = defaultdict(str)
            function_call_arguments_chunks: defaultdict[
                ResponseId, defaultdict[CallId, str]
            ] = defaultdict(lambda: defaultdict(str))
            async for data in conn:
                message = json.loads(data)  # type: RawMessage
                match message["type"]:  # type:
                    case "response.done":
                        if message["response"]["status"] == "failed":
                            print(  # noqa: T201
                                f"Failed: {message['response']['status_details']['error']}"
                            )
                    case "session.created":
                        current_session = message["session"]
                        self._session = {
                            key: current_session[key] if value == NotSet else value
                            for key, value in self._session.items()
                        }
                        await self._create_session_update(conn)
                    case "response.audio.done":
                        audio = audio_chunk_to_audio_segment(
                            audio_chunks.pop(message["response_id"])
                        )
                        await self._process_specific_receiver(audio, "audio")
                    case "response.audio.delta":
                        audio_chunks[message["response_id"]] += base64.b64decode(
                            message["delta"]
                        )
                        await self._process_specific_receiver(message, "audio_chunk")
                    case "response.text.done":
                        await self._process_specific_receiver(
                            text_chunks.pop(message["response_id"]), "text"
                        )
                        self._text_message_received = True
                    case "response.text.delta":
                        text_chunks[message["response_id"]] += message["delta"]
                        await self._process_specific_receiver(message, "text_chunk")
                    case "response.audio_transcript.done":
                        await self._process_specific_receiver(
                            audio_transcript_chunks[message["response_id"]],
                            "audio_transcript",
                        )
                        self._audio_transcript_received = True
                    case "response.audio_transcript.delta":
                        audio_transcript_chunks[message["response_id"]] += message[
                            "delta"
                        ]
                        await self._process_specific_receiver(
                            message, "audio_transcript_chunk"
                        )
                    case "response.function_call_arguments.delta":
                        function_call_arguments_chunks[message["response_id"]][
                            message["call_id"]
                        ] += message["delta"]
                        await self._process_specific_receiver(message, "tool_chunk")
                    case "response.function_call_arguments.done":
                        tool_name, response_id, call_id = (
                            message["name"],
                            message["response_id"],
                            message["call_id"],
                        )

                        tool_type_and_tool_schemas = self._temporary_tool_schemas.pop(
                            tool_name, []
                        )
                        if tool_type_and_tool_schemas:
                            tool_type, tool_schema = tool_type_and_tool_schemas.pop(0)
                        else:
                            tool_type, tool_schema = self._tool_schemas[tool_name]
                        function_call_arguments = function_call_arguments_chunks[
                            response_id
                        ].pop(call_id)
                        if not function_call_arguments_chunks[response_id]:
                            del function_call_arguments_chunks[response_id]
                        tool = tool_type.from_tool_call(
                            FunctionCallArguments(
                                call_id=call_id,
                                arguments=function_call_arguments,
                            )
                        )
                        await self._process_specific_function_call_handler(
                            conn, call_id, tool_name, tool
                        )

                # Call the receivers for all messages
                for receiver in self.receivers[None]:
                    await receiver(message, self.context)
        except asyncio.CancelledError:
            pass

    async def run(self) -> None:
        if self.is_running():
            raise RuntimeError("Already running")

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "OpenAI-Beta": "realtime=v1",
        }

        async for conn in connect(
            uri=f"wss://api.openai.com/v1/realtime?model={self._session['model']}",
            additional_headers=headers,
        ):
            try:
                receiver_task = asyncio.create_task(self._process_receiver(conn))
                sender_task = asyncio.create_task(self._process_sender(conn))
                await asyncio.gather(receiver_task, sender_task)
            except websockets.ConnectionClosed:
                continue

    def is_running(self) -> bool:
        return self._connection is not None
