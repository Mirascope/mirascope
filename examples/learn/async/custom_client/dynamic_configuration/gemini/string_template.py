from google.generativeai import GenerativeModel
from mirascope.core import gemini, prompt_template


@gemini.call("")
@prompt_template("Recommend a {genre} book")
async def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
    return {
        "client": GenerativeModel(model_name="gemini-1.5-flash"),
    }
