from mirascope.core import azure, BaseDynamicConfig, BaseMessageParam
from mirascope.tools import FileSystemToolkit
from pathlib import Path


@azure.call("gpt-4o-mini")
def write_blog_post(topic: str, output_file: Path) -> BaseDynamicConfig:
    toolkit = FileSystemToolkit(base_directory=output_file.parent)
    return {
        "messages": [
            BaseMessageParam(
                role="user",
                content=f"Write a blog post about '{topic}' as a '{output_file.name}'.",
            )
        ],
        "tools": toolkit.create_tools(),
    }


response = write_blog_post("machine learning", Path("introduction.html"))
if tool := response.tool:
    result = tool.call()
    print(result)