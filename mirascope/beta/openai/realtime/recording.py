import asyncio
import wave
from collections.abc import AsyncGenerator, Awaitable, Callable
from io import BytesIO
from queue import Empty, Queue
from typing import Any

import numpy
import numpy as np
import sounddevice as sd

from ._utils._audio import CHANNELS, FRAME_RATE


async def async_input(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)


def _create_buffer_from_recording(recording: numpy.ndarray) -> BytesIO:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16 is 2 bytes
        wf.setframerate(FRAME_RATE)
        wf.writeframes(recording.tobytes())
    buffer.seek(0)
    return buffer


async def record_as_stream(
    custom_blocking_event: Callable[..., Awaitable[...]] | None = None,
) -> AsyncGenerator[BytesIO, None]:
    event = asyncio.Event()
    data_queue = Queue()

    def callback(indata: np.ndarray, *args: Any) -> None:  # noqa: ANN401
        if event.is_set():
            raise sd.CallbackStop
        data_queue.put(indata.copy())

    stream = sd.InputStream(
        samplerate=FRAME_RATE, channels=CHANNELS, dtype="int16", callback=callback
    )

    async def blocking_event() -> None:
        if custom_blocking_event:
            await custom_blocking_event()
        else:
            while True:
                await asyncio.sleep(0.01)
        event.set()

    with stream:
        asyncio.create_task(blocking_event())
        accumulated_data = []
        accumulated_bytes = 0
        chunk_size_bytes = 32 * 1024  # 32KB
        while not event.is_set() or not data_queue.empty():
            try:
                indata_ = data_queue.get_nowait()
                accumulated_data.append(indata_)
                accumulated_bytes += indata_.nbytes

                if accumulated_bytes >= chunk_size_bytes:
                    data_to_yield = np.concatenate(accumulated_data, axis=0)

                    buffer = _create_buffer_from_recording(data_to_yield)
                    yield buffer

                    accumulated_data = []
                    accumulated_bytes = 0
            except Empty:
                await asyncio.sleep(0.01)

    while not data_queue.empty():
        yield data_queue.get_nowait()


async def record(custom_blocking_event: Callable[..., Awaitable[...]]) -> BytesIO:
    recording = []
    event = asyncio.Event()

    def callback(indata: numpy.ndarray, *args: Any) -> None:  # noqa: ANN401
        if event.is_set():
            raise sd.CallbackStop
        recording.append(indata.copy())

    stream = sd.InputStream(
        samplerate=FRAME_RATE, channels=CHANNELS, dtype="int16", callback=callback
    )

    with stream:
        await custom_blocking_event()
        event.set()

    recording = np.concatenate(recording, axis=0)

    return _create_buffer_from_recording(recording)
