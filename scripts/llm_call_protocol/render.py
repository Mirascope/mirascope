from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from typing_extensions import TypedDict

HERE = Path(__file__).parent
env = Environment(
    loader=FileSystemLoader(HERE),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=False,
)


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


result = env.get_template("llm_call_protocols.jinja2").render(
    providers=[
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
)

with Path(__file__).parent.joinpath("headers.py").open("r") as f:
    header = f.read()

with Path(__file__).parent.parent.joinpath("_call_protocol.py").open("w") as f:
    f.write(header + result)
