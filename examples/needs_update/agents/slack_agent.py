"""A slack bot agent that uses mirascope to generate responses to messages.
This example has basic short term memory for when the app is running and resets on restart.
"""

import asyncio
import os

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, ConfigDict
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"
SLACK_BOT_TOKEN = "xoxb-..."
SLACK_APP_TOKEN = "xapp-..."


class MiraBot(BaseModel):
    app: AsyncApp = AsyncApp(token=SLACK_BOT_TOKEN)
    history: list[ChatCompletionMessageParam] = []

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    @openai.call_async(model="gpt-4o", temperature=0)
    async def _step(self, input: str):
        """
        SYSTEM:
        You are an assistant that can help with a wide range of tasks and provide
        valuable insights and information on a wide range of topics.

        {self.history}

        USER:
        {input}
        """

    async def register_event_handlers(self):
        @self.app.event("message")
        async def handle_message_events(message, say, logger):
            response = await self._step(message["text"])
            if response.user_message_param:
                self.history.append(response.user_message_param)
            self.history.append(response.message_param)
            await say(response.content)

    async def start(self):
        handler = AsyncSocketModeHandler(self.app, SLACK_APP_TOKEN)
        await self.register_event_handlers()
        await handler.start_async()


if __name__ == "__main__":
    asyncio.run(MiraBot().start())
