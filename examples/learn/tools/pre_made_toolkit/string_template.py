from pathlib import Path

from mirascope import BaseDynamicConfig, llm, prompt_template
from mirascope.tools import FileSystemToolKit


@llm.call(provider="openai", model="gpt-4o-mini")
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
