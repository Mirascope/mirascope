"""A simple script for using RAG to ask questions about recent soccer results."""
import os

import numpy as np
import pandas as pd

from mirascope import OpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

soccer_info = [
    "Manchester City won the league, continuing their domestic dominance.",
    "In La Liga, FC Barcelona emerged victorious with a sturdy defense.",
    "Dortmund slipped up in the last matchday to hand Bayern the Bundesliga title.",
    "For the first time since Diego Maradona's days, Napoli lifted the Serie A trophy.",
]

chat = OpenAIChat()
embeddings_model = "text-embedding-ada-002"
embeddings = [
    chat.client.embeddings.create(model=embeddings_model, input=[text])
    .data[0]
    .embedding
    for text in soccer_info
]
df = pd.DataFrame({"texts": soccer_info, "embeddings": embeddings})


class SoccerPrompt(Prompt):
    """
    Here is some context about what happened in soccer in the 2022-23 season: {context}


    Based on this information, answer the following question: {question}
    """

    context: str
    question: str


def ask_soccer(query: str) -> str:
    """Answers a question about soccer from retrieved context."""
    query_embedding = (
        chat.client.embeddings.create(model=embeddings_model, input=[query])
        .data[0]
        .embedding
    )
    # Embedded texts are all the same length, so dot is equivalent to cosine
    df["similarities"] = df.embeddings.apply(lambda x: np.dot(x, query_embedding))
    most_similar = df.sort_values("similarities", ascending=False).iloc[0]["texts"]

    prompt = SoccerPrompt(context=most_similar, question=query)

    return str(chat.create(prompt))


countries = ["English", "Spanish", "German", "Italian"]
for country in countries:
    print(ask_soccer(f"Who won the {country} top flight?"))
