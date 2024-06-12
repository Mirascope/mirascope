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

from .models import BookRecommender

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


# Make sure csrf_exempt is removed for production use cases
@csrf_exempt
def recommend_book(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            book_recommender = BookRecommender.model_validate(data)
            book = book_recommender.extract()
            return JsonResponse(book.model_dump(), status=200)
        except ValidationError as e:
            return JsonResponse(e.errors(), status=400, safe=False)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)
