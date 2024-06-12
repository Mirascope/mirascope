"""
Flask + Mirascope example
Running Flask with Mirascope is the same as running Flask with Pydantic

Run with:
curl -X POST -H "Content-Type: application/json" -d '{"genre": "Fantasy"}' http://localhost:5000/books
"""

import os

from flask import Flask, jsonify, request
from pydantic import BaseModel, ValidationError

from mirascope.openai import OpenAICallParams, OpenAIExtractor

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

app = Flask(__name__)


class Book(BaseModel):
    title: str
    author: str


class BookRecommender(OpenAIExtractor[Book]):
    extract_schema: type[Book] = Book
    prompt_template = "Please recommend a {genre} book."

    genre: str

    call_params = OpenAICallParams(tool_choice="required")


@app.route("/books", methods=["POST"])
def root():
    """Generates a book based on provided `genre`."""
    try:
        book_recommender = BookRecommender.model_validate(request.get_json())
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(book_recommender.extract().model_dump()), 200


if __name__ == "__main__":
    app.run(debug=True)
