import re

from mirascope import llm, prompt_template


def parse_cot(response: llm.CallResponse) -> str:
    pattern = r"<thinking>.?*</thinking>.*?<output>(.*?)</output>"
    match = re.search(pattern, response.content, re.DOTALL)
    if not match:
        return response.content
    return match.group(1).strip()


@llm.call(provider="openai", model="gpt-4o-mini", output_parser=parse_cot)
@prompt_template(
    """
    First, output your thought process in <thinking> tags.
    Then, provide your final output in <output> tags.

    Question: {question}
    """
)
def chain_of_thought(question: str): ...


question = "Roger has 5 tennis balls. He buys 2 cans of 3. How many does he have now?"
output = chain_of_thought(question)
print(output)
