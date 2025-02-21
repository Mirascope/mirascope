from mirascope import AudioPart, BaseMessageParam, TextPart


def identify_book_prompt(audio_wave: bytes) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="Here's an audio book snippet:"),
                AudioPart(
                    type="audio",
                    media_type="audio/wav",
                    audio=audio_wave,
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
#             AudioPart(type='audio', media_type='audio/mp3', audio=b'...'),
#             TextPart(type="text", text="What book is this?"),
#         ],
#     )
# ]
