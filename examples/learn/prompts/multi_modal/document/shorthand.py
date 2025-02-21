from mirascope import DocumentPart, Messages, prompt_template


@prompt_template()
def recommend_book_prompt(previous_book_pdf: bytes) -> Messages.Type:
    return Messages.User(
        [
            "I just read this book:",
            DocumentPart(
                type="document",
                media_type="application/pdf",
                document=previous_book_pdf,
            ),
            "What should I read next?",
        ]
    )


print(recommend_book_prompt(b"..."))
# Output: [
#     BaseMessageParam(
#         role="user",
#         content=[
#             TextPart(type="text", text="I just read this book:"),
#             DocumentPart(type='document', media_type='application/pdf', document=b'...'),
#             TextPart(type="text", text="What should I read next?"),
#         ],
#     )
# ]
