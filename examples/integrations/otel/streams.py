from mirascope.core import openai, prompt_template
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@openai.call(
    model="gpt-4o-mini",
    stream=True,
    call_params={"stream_options": {"include_usage": True}},
)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str) -> None: ...


for chunk, _ in recommend_book("fantasy"):
    print(chunk.content, end="", flush=True)
