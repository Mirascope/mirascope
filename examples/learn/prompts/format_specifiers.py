from mirascope.core import BasePrompt, prompt_template


@prompt_template("Recommend a book cheaper than ${price:.2f}")
class BookRecommendationPrompt(BasePrompt):
    price: float


prompt = BookRecommendationPrompt(price=12.3456)
print(prompt)
# > Recommend a book cheaper than $12.34
