from mirascope import Messages, prompt_template
from PIL import Image


@prompt_template()
def recommend_book_prompt(previous_book: Image.Image) -> Messages.Type:
    return Messages.User(
        ["I just read this book:", previous_book, "What should I read next?"]
    )


with Image.open("...") as image:
    print(recommend_book_prompt(image))
# Output: [
#     BaseMessageParam(
#         role="user",
#         content=[
#             TextPart(type="text", text="I just read this book:"),
#             ImagePart(type="image", media_type="image/jpeg", image=b"...", detail=None),
#             TextPart(type="text", text="What should I read next?"),
#         ],
#     )
# ]
