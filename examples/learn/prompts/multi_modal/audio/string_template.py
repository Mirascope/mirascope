from mirascope.core import prompt_template


@prompt_template("Here's an audio book snippet: {audio_wav:audio} What book is this?")
def identify_book_prompt(audio_wav: bytes): ...


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
