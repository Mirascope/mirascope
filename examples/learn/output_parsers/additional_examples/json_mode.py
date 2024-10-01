import json

from mirascope.core import anthropic


def only_json(response: anthropic.AnthropicCallResponse) -> str:
    json_start = response.content.index("{")
    json_end = response.content.rfind("}")
    return response.content[json_start : json_end + 1]


@anthropic.call("claude-3-5-sonnet-20240620", json_mode=True, output_parser=only_json)
def json_extraction(text: str, fields: list[str]) -> str:
    return f"Extract {fields} from the following text: {text}"


json_response = json_extraction(
    text="The capital of France is Paris",
    fields=["capital", "country"],
)
print(json.loads(json_response))
