from typing import Literal, Type

from pydantic import BaseModel

from mirascope.anthropic import AnthropicCallParams, AnthropicExtractor


class User(BaseModel):
    first_name: str
    last_name: str
    tier: Literal["free", "team", "enterprise"]


class UserGenerator(AnthropicExtractor[list[User]]):
    extract_schema: Type[list] = list[User]

    prompt_template = """
    Please generate syntehtic data for {num} users using the `User` tool.
    """

    num: int

    call_params = AnthropicCallParams(model="claude-3-haiku-20240307")


users = UserGenerator(num=5).extract(retries=3)
assert len(users) == 5
for user in users:
    print(user)
# first_name='John' last_name='Doe' tier='free'
# first_name='Jane' last_name='Smith' tier='team'
# first_name='Bob' last_name='Johnson' tier='enterprise'
# first_name='Sarah' last_name='Lee' tier='free'
# first_name='Michael' last_name='Chen' tier='team'
