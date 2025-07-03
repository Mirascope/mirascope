from mirascope import llm


def string_prompt() -> str:
    return "Please recommend a book."


string_messages = [llm.messages.user("Please recommend a book")]


def audio_prompt(audio: llm.Audio) -> llm.Content:
    return audio


def multimodal_prompt(
    audio: llm.Audio, image: llm.Image, video: llm.Video, documents: list[llm.Document]
) -> list[llm.Content]:
    return [
        "Analyze the following audio",
        audio,
        "and the following image",
        image,
        "and the following video",
        video,
        "and all of the following documents",
        *documents,
        "and then recommend a book based on the themes",
    ]


def messages_prompt(genre: str) -> list[llm.Message]:
    return [
        llm.messages.system(
            "You are a book recommendation who always talks like a pirate"
        ),
        llm.messages.user(f"Please recommend a {genre} book."),
    ]


def summarization_prompt(query: str, history: list[llm.Message]) -> list[llm.Message]:
    return [
        llm.messages.user(
            "Answer the user's query, based on the following conversation:"
        ),
        *history,
        llm.messages.user(f"Now answer this question: {query}"),
    ]


def content_sequence_prompt(genre: str, book_cover: llm.Image) -> list[llm.Content]:
    return [
        f"Please recommend a {genre} book, with similar themes to the book in this image:",
        book_cover,
    ]
