from mirascope import prompt_template


@prompt_template(
    "I just read this book: {previous_book:image} What should I read next?"
)
def recommend_book_prompt(previous_book: bytes): ...


print(recommend_book_prompt(b"..."))
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
