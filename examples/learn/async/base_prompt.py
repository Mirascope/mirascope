import asyncio

from mirascope.core import BasePrompt, openai, prompt_template


@prompt_template("Analyze the sentiment of the following text: {text}")
class SentimentAnalysisPrompt(BasePrompt):
    text: str


async def main():
    prompt = SentimentAnalysisPrompt(text="I love using Mirascope!")
    result = await prompt.run_async(openai.call(model="gpt-4o-mini"))
    print(result.content)


asyncio.run(main())
