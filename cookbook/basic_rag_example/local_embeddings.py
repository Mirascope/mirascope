"""A simple script for using RAG to ask questions about recent soccer results."""
import os

import numpy as np
import openai
import pandas as pd

from mirascope import OpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

soccer_info = [
    "Manchester City won the league, continuing their domestic dominance.",
    "In La Liga, FC Barcelona emerged victorious with a sturdy defense.",
    "Dortmund slipped up in the last matchday to hand Bayern the Bundesliga title.",
    "For the first time since Diego Maradona's days, Napoli lifted the Serie A trophy.",
]

client = openai.OpenAI()
embeddings_model = "text-embedding-ada-002"
df = pd.DataFrame(columns=["texts", "embeddings"])
for text in soccer_info:
    res = (
        client.embeddings.create(model=embeddings_model, input=[text]).data[0].embedding
    )
    new_row = pd.DataFrame({"texts": [text], "embeddings": [res]})
    df = pd.concat([df, new_row], ignore_index=True)


class SoccerPrompt(Prompt):
    """
    Here is some context about what happened in soccer in the 2022-23 season: {context}


    Based on this information, answer the following question: {question}
    """

    context: str
    question: str


model = OpenAIChat()


def ask_soccer(query):
    query_embedding = (
        client.embeddings.create(model=embeddings_model, input=[query])
        .data[0]
        .embedding
    )
    df["similarities"] = df.embeddings.apply(lambda x: np.dot(x, query_embedding))
    most_similar = df.sort_values("similarities", ascending=False).iloc[0]["texts"]

    prompt = SoccerPrompt(context=most_similar, question=query)
    res = model.create(prompt)
    print(str(res))


for country in ["English", "Spanish", "German", "Italian"]:
    ask_soccer(f"Who won the {country} top flight?")
