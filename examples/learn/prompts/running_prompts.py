from mirascope.core import BasePrompt, anthropic, openai, prompt_template


@prompt_template("Recommend a {genre} book")
class BookRecommendationPrompt(BasePrompt):
    genre: str


prompt = BookRecommendationPrompt(genre="fantasy")

# Running the prompt with OpenAI
print(prompt.run(openai.call(model="gpt-4o-mini")))
# > Sure! If you're looking for a captivating fantasy novel, I recommend...

# Running the prompt with Anthropic
print(prompt.run(anthropic.call(model="claude-3-5-sonnet-20240620")))
# > There are many great fantasy books to choose from, but...
