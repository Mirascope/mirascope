"""
This example demonstrates how to use Nimble as a tool to search for products on Amazon
"""

import os

import requests

from mirascope.core import openai

NIMBLE_TOKEN = "YOUR_NIMBLE_TOKEN"
os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


def nimble_amazon(question: str):
    """
    Use Nimble to search for products on Amazon.
    """
    url = "https://api.webit.live/api/v1/realtime/web"
    headers = {
        "Authorization": f"Basic {NIMBLE_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "parse": True,
        "vendor": "amazon",
        "url": f"https://www.amazon.com/s?k={question}",
        "format": "json",
        "render": True,
        "country": "US",
        "locale": "en",
    }

    response = requests.post(url, headers=headers, json=data)
    json_response = response.json()
    products = [
        {
            "product_name": result.get("productName", ""),
            "price": result.get("price", ""),
            "asin": result.get("asin", ""),
            "rating": result.get("rating", ""),
            "product_url": result.get("productUrl", ""),
        }
        for result in json_response["parsing"]["entities"]["SearchResult"]
    ]
    return products


@openai.call(model="gpt-4o", tools=[nimble_amazon], tool_choice="required")
def amazon_searcher(question: str):
    """
    SYSTEM:
    You are an AI assistant that can search for products on Amazon.
    Given an item, use the tool to search for products on Amazon.

    USER:
    {question}
    """


@openai.call(model="gpt-4o")
def product_recommender(products: list[dict], question: str):
    """
    SYSTEM:
    You are an AI assistant that can recommend products on Amazon.
    Given a list of {question} on Amazon, recommend the best one.

    Products:
    {products}

    USER:
    Recommend me the product with the best value.
    """


question = "mirascope"
results = amazon_searcher(question=question)
if tool := results.tool:
    products = tool.call()
    response = product_recommender(products=products, question=question)
    print(response.content)
