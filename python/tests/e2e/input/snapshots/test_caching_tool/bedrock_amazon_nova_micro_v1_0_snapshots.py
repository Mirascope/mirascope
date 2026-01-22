from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": """\
<thinking> The user has greeted the bot in a Star Wars style. The bot should respond in kind, using a similar style and invoking a Star Wars character to acknowledge the greeting. </thinking>


**ToolCall (star_wars_tool):** {}

**ToolCall (star_wars_tool):** {}

**ToolCall (star_wars_tool):** {}\
""",
        "usage1": {
            "input_tokens": 4103,
            "output_tokens": 72,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "None",
            "total_tokens": 4175,
        },
        "response2": """\
<thinking> The User's request is about suggesting a breakfast option. The available tools do not include a function for suggesting meals. Therefore, I will provide a general recommendation based on common breakfast choices.</thinking>

<thinking> Based on common breakfast choices, a balanced breakfast might include something like oatmeal with fruits, a smoothie, or a breakfast burrito. However, without specific dietary preferences or restrictions from the User, I will suggest a general and healthy option.</thinking>
You might want to have a bowl of oatmeal with some fresh fruits for breakfast. Oatmeal is a great source of fiber and can help keep you full throughout the morning. Adding fruits like berries or bananas can provide additional nutrients and natural sweetness.\
""",
        "usage2": {
            "input_tokens": 4107,
            "output_tokens": 151,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "None",
            "total_tokens": 4258,
        },
    }
)
