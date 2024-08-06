"""
Flask + Mirascope example
Running Flask with Mirascope is the same as running Flask with Pydantic

Run with:
curl -X POST -H "Content-Type: application/json" -d '{"genre": "Fantasy"}' http://localhost:5000/books
"""

import os

from flask import Flask, jsonify, request
from pydantic import BaseModel, ValidationError

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"

app = Flask(__name__)


class Book(BaseModel):
    title: str
    author: str


@openai.call(model="gpt-4o", response_model=Book)
def recommend_book(genre: str):
    """Please recommend a {genre} book."""


@app.route("/books", methods=["POST"])
def root():
    """Generates a book based on provided `genre`."""
    try:
        book_recommender = recommend_book(request.get_json())
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(book_recommender.model_dump()), 200


if __name__ == "__main__":
    app.run(debug=True)
