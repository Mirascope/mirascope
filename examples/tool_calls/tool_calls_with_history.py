"""
This example shows how to use Mirascope to call tools and append the tool call to history.
"""

import os
from typing import Literal

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


class WeatherBroadcaster(BaseModel):
    history: list[ChatCompletionMessageParam] = []

    def get_current_weather(
        self, location: str, unit: Literal["celsius", "fahrenheit"] = "fahrenheit"
    ):
        """Get the current weather in a given location."""
        if "tokyo" in location.lower():
            return f"It is 10 degrees {unit} in Tokyo, Japan"
        elif "san francisco" in location.lower():
            return f"It is 72 degrees {unit} in San Francisco, CA"
        elif "paris" in location.lower():
            return f"It is 22 degress {unit} in Paris, France"
        else:
            return f"I'm not sure what the weather is like in {location}"

    @openai.call(model="gpt-4o")
    def _step(self, question: str):
        """
        MESSAGES: {self.history}
        USER: {question}
        """
        return {"tools": [self.get_current_weather]}

    def get_forecast(self, question: str):
        response = self._step(question)
        self.history += [response.user_message_param, response.message_param]
        if tool := response.tool:
            output = tool.call()
            self.history += response.tool_message_params([(tool, output)])
            return self.get_forecast(question)
        else:
            return response.content


# Make the first call to the LLM
forecast = WeatherBroadcaster(history=[])
response = forecast.get_forecast(question="What's the weather in Tokyo Japan?")
print(response)
