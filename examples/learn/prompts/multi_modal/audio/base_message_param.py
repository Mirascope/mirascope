from mirascope.core import BaseMessageParam
from mirascope.core.base import AudioPart, TextPart


def identify_book_prompt(audio_wav: bytes) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Here's an audio book snippet:"),
                AudioPart(
                    type="audio",
                    media_type="audio/wav",
                    audio=audio_wav,
                ),
                TextPart(type="text", text="What book is this?"),
            ],
        )
    ]


print(identify_book_prompt(b"..."))
# Output: [
#     BaseMessageParam(
#         role="user",
#         content=[
#             TextPart(type="text", text="Here's an audio book snippet:"),
#             AudioPart(type='audio', media_type='audio/wav', audio=b'...'),
#             TextPart(type="text", text="What book is this?"),
#         ],
#     )
# ]
