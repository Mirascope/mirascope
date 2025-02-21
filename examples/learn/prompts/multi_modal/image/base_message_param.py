from mirascope import BaseMessageParam, ImagePart, TextPart


def recommend_book_prompt(previous_book_jpeg: bytes) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=[
                TextPart(type="text", text="I just read this book:"),
                ImagePart(
                    type="image",
                    media_type="image/jpeg",
                    image=previous_book_jpeg,
                    detail=None,
                ),
                TextPart(type="text", text="What should I read next?"),
            ],
        )
    ]


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
