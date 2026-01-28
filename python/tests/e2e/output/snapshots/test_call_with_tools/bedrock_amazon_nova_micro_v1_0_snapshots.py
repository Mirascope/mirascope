from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 591,
                "output_tokens": 123,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 714,
            },
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=[
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='<thinking> I need to retrieve secrets associated with the passwords "mellon" and "radiance". To do this, I will need to call the `secret_retrieval_tool` twice, once for each password. I will provide the password argument for each call.</thinking>\n'
                        ),
                        ToolCall(
                            id="tooluse_nz0CoSg6TyuVDvWTCaatSw",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="tooluse_KBNwKhm1RwK4iTLuHbyOtg",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="tooluse_nz0CoSg6TyuVDvWTCaatSw",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="tooluse_KBNwKhm1RwK4iTLuHbyOtg",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<thinking> The `secret_retrieval_tool` has returned the secrets associated with the passwords "mellon" and "radiance". The secret for the password "mellon" is "Welcome to Moria!" and for the password "radiance" is "Life before Death". Now I will provide these secrets to the User.</thinking>

You have successfully retrieved the secrets associated with the passwords "mellon" and "radiance". Here are the results:
- For the password "mellon": "Welcome to Moria!"
- For the password "radiance": "Life before Death"\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "secret_retrieval_tool",
                    "description": "A tool that requires a password to retrieve a secret.",
                    "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 610,
                "output_tokens": 92,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 702,
            },
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=[
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='<thinking> To retrieve secrets associated with the given passwords, I need to use the `secret_retrieval_tool` with each password. However, I need to make separate calls for each password as the tool does not support multiple passwords in a single call. First, I will retrieve the secret for the password "mellon" and then for "radiance". </thinking>\n'
                        ),
                        ToolCall(
                            id="tooluse__Mr-OCp3R0mr3oW_8jfiUg",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="tooluse_M7S2gH0dTnGUFJsNKL5PIQ",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="tooluse__Mr-OCp3R0mr3oW_8jfiUg",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="tooluse_M7S2gH0dTnGUFJsNKL5PIQ",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<thinking> I have received the results for both passwords. The secret for the password "mellon" is "Welcome to Moria!" and for the password "radiance" is "Life before Death". Now, I will compile and present these secrets to the user. </thinking> \n\

Here are the secrets associated with the given passwords:
- Password "mellon": "Welcome to Moria!"
- Password "radiance": "Life before Death"\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "secret_retrieval_tool",
                    "description": "A tool that requires a password to retrieve a secret.",
                    "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "finish_reason": None,
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=[
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='<thinking> To retrieve the secrets associated with each of the provided passwords "mellon" and "radiance", I will need to use the `secret_retrieval_tool` with each password. Since the tool requires the password as an argument, I will create two separate tool calls, one for each password. </thinking>\n'
                        ),
                        ToolCall(
                            id="tooluse_jmYwyYtsQxiOee3FyiEBog",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="tooluse_wwdyV5DhQ4yhJbQiWcoZmw",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="tooluse_jmYwyYtsQxiOee3FyiEBog",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="tooluse_wwdyV5DhQ4yhJbQiWcoZmw",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<thinking> The `secret_retrieval_tool` has successfully retrieved the secrets associated with the provided passwords. The secret for the password "mellon" is "Welcome to Moria!" and for the password "radiance" is "Life before Death". Now I will compile these results and present them to the User. </thinking>

Here are the secrets associated with each password:
- Password: mellon, Secret: Welcome to Moria!
- Password: radiance, Secret: Life before Death\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "secret_retrieval_tool",
                    "description": "A tool that requires a password to retrieve a secret.",
                    "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 600,
                "output_tokens": 103,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 703,
            },
            "n_chunks": 105,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "finish_reason": None,
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=[
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='<thinking> To retrieve the secrets associated with each of the provided passwords "mellon" and "radiance", I will need to use the `secret_retrieval_tool` with each password. Since the tool requires the password as an argument, I will create two separate tool calls, one for each password. </thinking>\n'
                        ),
                        ToolCall(
                            id="tooluse_jmYwyYtsQxiOee3FyiEBog",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="tooluse_wwdyV5DhQ4yhJbQiWcoZmw",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="tooluse_jmYwyYtsQxiOee3FyiEBog",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="tooluse_wwdyV5DhQ4yhJbQiWcoZmw",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<thinking> The `secret_retrieval_tool` has successfully retrieved the secrets associated with the provided passwords. The secret for the password "mellon" is "Welcome to Moria!" and for the password "radiance" is "Life before Death". Now I will compile these results and present them to the User. </thinking>

Here are the secrets associated with each password:
- Password: mellon, Secret: Welcome to Moria!
- Password: radiance, Secret: Life before Death\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "secret_retrieval_tool",
                    "description": "A tool that requires a password to retrieve a secret.",
                    "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 600,
                "output_tokens": 103,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 703,
            },
            "n_chunks": 105,
        }
    }
)
