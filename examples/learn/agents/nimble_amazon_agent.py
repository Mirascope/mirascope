import requests
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import openai, prompt_template

NIMBLE_TOKEN = "YOUR_NIMBLE_TOKEN"


def amazon_search(question: str):
    """Use Nimble to search for products on Amazon."""
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


class NimbleAmazonBot(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    @openai.call(model="gpt-3.5-turbo", tools=[amazon_search])
    @prompt_template(
        """
        SYSTEM: Answer the user's question using your `amazon_search` tool.
        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _call(self, query: str): ...

    def _step(self, query: str):
        response = self._call(query)
        self.history += [response.user_message_param, response.message_param]
        if tools := response.tools:
            for tool in tools:
                self.history += response.tool_message_params([(tool, tool.call())])
            return self._step("")
        else:
            return response.content

    def run(self):
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            response = self._step(query)
            print(f"(Assistant): {response}")


bot = NimbleAmazonBot()
bot.run()
