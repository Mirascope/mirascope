"""
Mirascope + Django extraction example

Run with:
python manage.py runserver
curl -X POST -H "Content-Type: application/json" -d '{"genre": "Fantasy"}' http://localhost:8000/books
"""

import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError

from mirascope.core import openai

from .models import Book

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai.call(model="gpt-4o", response_model=Book)
def recommend_book_call(genre: str):
    """Please recommend a {genre} book."""


# Make sure csrf_exempt is removed for production use cases
@csrf_exempt
def recommend_book(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            book = recommend_book_call(data)
            return JsonResponse(book.model_dump(), status=200)
        except ValidationError as e:
            return JsonResponse(e.errors(), status=400, safe=False)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)
