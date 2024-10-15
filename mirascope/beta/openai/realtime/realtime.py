from __future__ import annotations

import asyncio
import base64
import inspect
import json
import os
from collections.abc import Callable
from io import BytesIO
from typing import (
    Any,
    Literal,
    NotRequired,
    TypeAlias,
    TypedDict,
    TypeVar,
)

import websockets
from black.trans import defaultdict
from pydub import AudioSegment
from websockets.asyncio.client import ClientConnection, connect

from mirascope.beta.openai.realtime._utils._audio import (
    async_audio_input_audio_buffer_append_event,
    async_audio_to_item_create_event,
    audio_chunk_to_audio_segment,
)

from ._utils._protocols import ReceiverFunc, SenderFunc

ResponseType: TypeAlias = Literal[
    "text",
    "audio",
    "text_chunk",
    "audio_chunk",
    "audio_transcript",
    "audio_transcript_chunk",
]


_ResponseT = TypeVar("_ResponseT")
_ConnectionT = TypeVar("_ConnectionT")
# TODO: Improve the type of response
Response: TypeAlias = Any


class RawMessage(TypedDict, total=False):
    event_id: str
    type: str
    item: NotRequired[dict]
    delta: NotRequired[str]


class Sender(TypedDict):
    func: SenderFunc[_ResponseT]
    wait_for_text_response: bool
    wait_for_audio_transcript_response: bool


NotSet = object()


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
        tools: list[Any] | None = NotSet,
    ) -> None:
        self.senders: list[Sender] = []
        self.receivers: defaultdict[ResponseType, ReceiverFunc] = defaultdict(list)
        self._connection: connect | None = None
        self.context = context or {}
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
            "tools": tools,
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
    ) -> Callable[[SenderFunc[_ResponseT]], SenderFunc[_ResponseT]]:
        def inner(func: SenderFunc[_ResponseT]) -> SenderFunc[_ResponseT]:
            self.senders.append(
                {
                    "func": func,
                    "wait_for_text_response": wait_for_text_response,
                    "wait_for_audio_transcript_response": wait_for_audio_transcript_response,
                }
            )
            return func

        return inner

    def receiver(
        self, response_type: ResponseType
    ) -> Callable[[ReceiverFunc[_ResponseT]], ReceiverFunc]:
        def inner(func: ReceiverFunc[_ResponseT]) -> ReceiverFunc[_ResponseT]:
            self.receivers[response_type].append(func)
            return func

        return inner

    async def _create_response(self, conn: ClientConnection) -> None:
        await self._send_event(conn, {"type": "response.create"})

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

    async def _create_session_update(self, conn: ClientConnection) -> None:
        await self._send_event(
            conn,
            {
                "type": "session.update",
                "session": self._session,
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
                async for message in sender["func"](self.context):
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
            else:
                message = await sender["func"](self.context)
                match message:
                    case BytesIO() | bytes():
                        event = await async_audio_to_item_create_event(message)
                        await self._send_event(conn, event)
                    case str():
                        await self._create_conversation_item_create(conn, message)
                    case _:
                        continue
            await self._create_response(conn)
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

    async def _process_specific_receiver(
        self, message: dict[str, Any] | AudioSegment, response_type: ResponseType
    ) -> None:
        for receiver in self.receivers[response_type]:
            await receiver(message, self.context)

    async def _process_receiver(self, conn: ClientConnection) -> None:
        try:
            audio_chunk: bytes = b""
            text_chunk: str = ""
            audio_transcript_chunk: str = ""
            async for data in conn:
                message = json.loads(data)  # type: RawMessage
                match message["type"]:  # type:
                    case "session.created":
                        current_session = message["session"]
                        self._session = {
                            key: current_session[key] if value == NotSet else value
                            for key, value in self._session.items()
                        }
                        await self._create_session_update(conn)
                    case "response.audio.done":
                        audio = audio_chunk_to_audio_segment(audio_chunk)
                        await self._process_specific_receiver(audio, "audio")
                        audio_chunk = b""
                    case "response.audio.delta":
                        audio_chunk += base64.b64decode(message["delta"])
                        await self._process_specific_receiver(message, "audio_chunk")
                    case "response.text.done":
                        await self._process_specific_receiver(text_chunk, "text")
                        text_chunk = ""
                        self._text_message_received = True
                    case "response.text.delta":
                        text_chunk += message["delta"]
                        await self._process_specific_receiver(message, "text_chunk")
                    case "response.audio_transcript.done":
                        await self._process_specific_receiver(
                            audio_transcript_chunk, "audio_transcript"
                        )
                        audio_transcript_chunk = ""
                        self._audio_transcript_received = True
                    case "response.audio_transcript.delta":
                        audio_transcript_chunk += message["delta"]
                        await self._process_specific_receiver(
                            audio_transcript_chunk, "audio_transcript_chunk"
                        )

                    # TODO: Add more cases like "response.function_call_arguments.done"

                # Call the receivers for all messages
                for receiver in self.receivers[None]:
                    await receiver(message, self.context)
        except asyncio.CancelledError:
            pass

    async def run(self) -> None:
        if self.is_running():
            raise RuntimeError("Already running")

        headers = {
            "Authorization": f"Bearer {os.environ["OPENAI_API_KEY"]}",
            "OpenAI-Beta": "realtime=v1",
        }

        async for conn in connect(
            uri=f"wss://api.openai.com/v1/realtime?model={self._session["model"]}",
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
