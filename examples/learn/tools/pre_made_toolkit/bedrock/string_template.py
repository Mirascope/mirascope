from pathlib import Path

from mirascope.core import BaseDynamicConfig, bedrock, prompt_template
from mirascope.tools import FileSystemToolKit


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Write a blog post about '{topic}' as a '{output_file.name}'.")
def write_blog_post(topic: str, output_file: Path) -> BaseDynamicConfig:
    toolkit = FileSystemToolKit(base_directory=output_file.parent)
    return {
        "tools": toolkit.create_tools(),
    }


response = write_blog_post("machine learning", Path("introduction.html"))
if tool := response.tool:
    result = tool.call()
    print(result)
