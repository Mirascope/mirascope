import asyncio
from datetime import datetime

import aiohttp
import requests
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import openai, prompt_template

NIMBLE_TOKEN = "YOUR_NIMBLE_API_KEY"


class LocalizedRecommender(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    async def _nimble_google_maps_places(
        self, session: aiohttp.ClientSession, place_id: str
    ):
        """
        Use Nimble to get the details of a place on Google Maps.
        """
        url = "https://api.webit.live/api/v1/realtime/serp"
        headers = {
            "Authorization": f"Basic {NIMBLE_TOKEN}",
            "Content-Type": "application/json",
        }
        place_data = {
            "parse": True,
            "search_engine": "google_maps_place",
            "place_id": place_id,
            "domain": "com",
            "format": "json",
            "render": True,
            "country": "US",
            "locale": "en",
        }
        async with session.get(url, json=place_data, headers=headers) as response:
            data = await response.json()
            result = data["parsing"]["entities"]["Place"][0]
            return {
                "opening_hours": result.get("place_information", {}).get(
                    "opening_hours", ""
                ),
                "rating": result.get("rating", ""),
                "name": result.get("title", ""),
            }

    async def _nimble_google_maps(self, latitude: float, longitude: float, query: str):
        """
        Use Nimble to search for places on Google Maps.
        """
        url = "https://api.webit.live/api/v1/realtime/serp"
        headers = {
            "Authorization": f"Basic {NIMBLE_TOKEN}",
            "Content-Type": "application/json",
        }
        search_data = {
            "parse": True,
            "search_engine": "google_maps_search",
            "query": query,
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "domain": "com",
            "format": "json",
            "render": True,
            "country": "US",
            "locale": "en",
        }
        search_response = requests.post(url, headers=headers, json=search_data)
        search_json_response = search_response.json()
        search_results = [
            {
                "place_id": result.get("place_id", ""),
            }
            for result in search_json_response["parsing"]["entities"]["SearchResult"]
        ]
        results = []
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._nimble_google_maps_places(session, results.get("place_id", ""))
                for results in search_results
            ]
            results = await asyncio.gather(*tasks)
        return results

    async def _get_current_date(self):
        """Get the current date and time."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def _get_coordinates_from_location(self, location_name: str):
        """Get the coordinates of a location."""
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location_name, "format": "json", "limit": 1}
        headers = {"User-Agent": "mirascope/1.0"}
        response = requests.get(base_url, params=params, headers=headers)
        data = response.json()

        if data:
            latitude = data[0].get("lat")
            longitude = data[0].get("lon")
            return f"Latitude: {latitude}, Longitude: {longitude}"
        else:
            return "No location found, ask me about a specific location."

    @openai.call(model="gpt-4o", stream=True)
    @prompt_template(
        """
        SYSTEM:
        You are a local guide that recommends the best places to visit in a place.
        Use the `_get_current_date` function to get the current date.
        Use the `_get_coordinates_from_location` function to get the coordinates of a location if you need it.
        Use the `_nimble_google_maps` function to get the best places to visit in a location based on the users query.

        MESSAGES: {self.history}
        USER: {question}
        """
    )
    async def _step(self, question: str) -> openai.OpenAIDynamicConfig:
        return {
            "tools": [
                self._get_current_date,
                self._get_coordinates_from_location,
                self._nimble_google_maps,
            ]
        }

    async def _get_response(self, question: str):
        response = await self._step(question)
        tool_call = None
        output = None
        async for chunk, tool in response:
            if tool:
                output = await tool.call()
                tool_call = tool
            else:
                print(chunk.content, end="", flush=True)
        if response.user_message_param:
            self.history.append(response.user_message_param)
        self.history.append(response.message_param)
        if tool_call and output:
            self.history += response.tool_message_params([(tool_call, str(output))])
            return await self._get_response(question)
        return

    async def run(self):
        while True:
            question = input("(User): ")
            if question == "exit":
                break
            print("(Assistant): ", end="", flush=True)
            await self._get_response(question)
            print()


recommender = LocalizedRecommender(history=[])
asyncio.run(recommender.run())
