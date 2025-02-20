from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import ChatRequestMessage
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint="YOUR_ENDPOINT", credential=AzureKeyCredential("YOUR_KEY")
)


def recommend_book(genre: str) -> str:
    completion = client.complete(
        model="gpt-4o-mini",
        messages=[
            ChatRequestMessage({"role": "user", "content": f"Recommend a {genre} book"})
        ],
    )
    message = completion.choices[0].message
    return message.content if message.content is not None else ""


output = recommend_book("fantasy")
print(output)
