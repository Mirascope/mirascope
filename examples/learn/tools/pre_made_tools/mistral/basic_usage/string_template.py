from mirascope.core import mistral, prompt_template
from mirascope.tools import DuckDuckGoSearch


@mistral.call("mistral-large-latest", tools=[DuckDuckGoSearch])
@prompt_template("Recommend a {genre} book and summarize the story")
def research(genre: str): ...


response = research("fantasy")
if tool := response.tool:
    print(tool.call())
