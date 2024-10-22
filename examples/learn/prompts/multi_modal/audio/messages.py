import wave
from mirascope.core import prompt_template, Messages


@prompt_template()
def identify_book_prompt(audio_wav: wave.Wave_read) -> Messages.Type:
    return Messages.User(
        ["Here's an audio book snippet:", audio_wav, "What book is this?"]
    )


with open("....", "rb") as f, wave.open(f) as audio:
    print(identify_book_prompt(audio))
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
