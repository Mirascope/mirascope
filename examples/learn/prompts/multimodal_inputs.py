from mirascope.core import BasePrompt, prompt_template


@prompt_template("I just read this book: {book:image}. What should I read next?")
class BookRecommendationPrompt(BasePrompt):
    book: str | bytes


url = "https://upload.wikimedia.org/wikipedia/en/5/56/TheNameoftheWind_cover.jpg"
prompt = BookRecommendationPrompt(book=url)
print(prompt.message_params())
# > [BaseMessageParam(
#       role='user',
#       content=[
#           TextPart(type='text', text='I just read this book:'),
#           ImagePart(
#               type='image',
#               media_type='image/jpeg',
#               image=b'...',
#               detail=None
#           ),
#           TextPart(type='text', text='. What should I read next?')
#       ]
#   )]
