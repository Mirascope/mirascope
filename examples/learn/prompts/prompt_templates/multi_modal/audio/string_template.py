from mirascope.core import prompt_template


@prompt_template("Here's an audio book snippet: {mp3:audio} What book is this?")
def identify_book_prompt(audio_mp3: bytes): ...


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
