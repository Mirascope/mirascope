from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from typing_extensions import TypedDict

WORK_DIR = Path(__file__).parent
PROJECT_ROOT = WORK_DIR.parents[1]
LLM_PACKAGE = PROJECT_ROOT / "mirascope" / "llm"
OUTPUT_FILE = LLM_PACKAGE / "_call_protocol.py"


class Provider(TypedDict):
    name: str
    response: str
    response_chunk: str
    base_tool: str
    base_stream: str
    base_dynamic_config: str
    async_base_dynamic_config: str
    base_call_param: str
    sync_base_client: str
    async_base_client: str
    same_sync_and_async_base_client: str


PROVIDERS = [
    Provider(
        name="openai",
        response="ChatCompletion",
        response_chunk="ChatCompletionChunk",
        base_stream="Stream[ChatCompletion, ChatCompletionChunk]",
        base_tool="OpenAITool",
        base_dynamic_config="OpenAIDynamicConfig",
        async_base_dynamic_config="AsyncOpenAIDynamicConfig",
        base_call_param="BaseCallParams",
        sync_base_client="OpenAI | AzureOpenAI",
        async_base_client="AsyncOpenAI | AsyncAzureOpenAI",
        same_sync_and_async_base_client="None",
    ),
]


def generate() -> None:
    env = Environment(
        loader=FileSystemLoader(WORK_DIR),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )

    result = env.get_template("llm_call_protocols.jinja2").render(providers=PROVIDERS)

    header = WORK_DIR.joinpath("headers.py").read_text()
    OUTPUT_FILE.write_text(header + result)


if __name__ == "__main__":
    generate()
