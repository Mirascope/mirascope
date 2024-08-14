from mirascope.core import BasePrompt, prompt_template


@prompt_template(
    "I just read this book: {book:image(detail=high)}. What should I read next?"
)
class BookRecommendationPrompt(BasePrompt):
    book: str | bytes


url = "https://upload.wikimedia.org/wikipedia/en/5/56/TheNameoftheWind_cover.jpg"
prompt = BookRecommendationPrompt(book=url)
print(prompt.message_params())
# > [BaseMessageParam(
#       role='user',
#       content=[
#           ...
#           ImagePart(
#               ...
#               detail='high'
#           ),
#           ...
#       ]
#   )]
