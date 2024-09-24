from mirascope.core import BaseMessageParam
from mirascope.core.base import AudioPart, TextPart


def identify_book_prompt(audio_mp3: bytes) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Here's an audio book snippet:"),
                AudioPart(
                    type="audio",
                    media_type="audio/mp3",
                    audio=audio_mp3,
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
#             ImagePart(type="image", media_type="image/jpeg", image=b"...", detail=None),
#             TextPart(type="text", text="What book is this?"),
#         ],
#     )
# ]
