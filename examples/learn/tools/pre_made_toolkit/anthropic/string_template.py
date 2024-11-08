from pathlib import Path

from mirascope.core import BaseDynamicConfig, anthropic, prompt_template
from mirascope.tools import FileSystemToolKit


@anthropic.call("claude-3-5-sonnet-20240620")
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
