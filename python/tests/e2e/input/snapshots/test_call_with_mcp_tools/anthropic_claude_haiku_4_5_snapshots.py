from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-haiku-4-5",
            "provider_model_name": "claude-haiku-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 1628,
                "output_tokens": 305,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=1628, output_tokens=305, server_tool_use=None, service_tier='standard')",
                "total_tokens": 1933,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="You have access to MCP tools. Use them as needed."
                    )
                ),
                UserMessage(
                    content=[
                        Text(
                            text="Please call the greet tool with name 'Mirascope', then call the answer_ultimate_question tool. Finally, try using the process_answer tool to see what it does. Report what you learn from all tools."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="I'll call these tools in sequence for you. Let me start with the first two tools, then use their results with the third tool."
                        ),
                        ToolCall(
                            id="toolu_01EXNZbjro89baFVduagcmUS",
                            name="greet",
                            args='{"name": "Mirascope"}',
                        ),
                        ToolCall(
                            id="toolu_01H3qMv9XPQWxwYJGPbdq91C",
                            name="answer_ultimate_question",
                            args="{}",
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-haiku-4-5",
                    provider_model_name="claude-haiku-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "I'll call these tools in sequence for you. Let me start with the first two tools, then use their results with the third tool.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01EXNZbjro89baFVduagcmUS",
                                "input": {"name": "Mirascope"},
                                "name": "greet",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_01H3qMv9XPQWxwYJGPbdq91C",
                                "input": {},
                                "name": "answer_ultimate_question",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01EXNZbjro89baFVduagcmUS",
                            name="greet",
                            value=[
                                {
                                    "type": "text",
                                    "text": "Welcome to Zombo.com, Mirascope",
                                    "annotations": None,
                                    "meta": None,
                                }
                            ],
                        ),
                        ToolOutput(
                            id="toolu_01H3qMv9XPQWxwYJGPbdq91C",
                            name="answer_ultimate_question",
                            value=[
                                {
                                    "type": "text",
                                    "text": """\
{
  "answer": 42,
  "question": "What is the answer to life, the universe, and everything?",
  "computed_by": {
    "name": "Deep Thought",
    "years_computed": 7500000
  }
}\
""",
                                    "annotations": None,
                                    "meta": None,
                                }
                            ],
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="Great! Now I'll use the answer data from the second tool to call the process_answer tool:"
                        ),
                        ToolCall(
                            id="toolu_01TQByfwngEjeFsRYDscMTrf",
                            name="process_answer",
                            args='{"answer_data": {"answer": 42, "question": "What is the answer to life, the universe, and everything?", "computed_by": {"name": "Deep Thought", "years_computed": 7500000}}}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-haiku-4-5",
                    provider_model_name="claude-haiku-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "Great! Now I'll use the answer data from the second tool to call the process_answer tool:",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01TQByfwngEjeFsRYDscMTrf",
                                "input": {
                                    "answer_data": {
                                        "answer": 42,
                                        "question": "What is the answer to life, the universe, and everything?",
                                        "computed_by": {
                                            "name": "Deep Thought",
                                            "years_computed": 7500000,
                                        },
                                    }
                                },
                                "name": "process_answer",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01TQByfwngEjeFsRYDscMTrf",
                            name="process_answer",
                            value=[
                                {
                                    "type": "text",
                                    "text": "The answer 42 to 'What is the answer to life, the universe, and everything?' was computed by Deep Thought over 7,500,000 years",
                                    "annotations": None,
                                    "meta": None,
                                }
                            ],
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
## Report on Tool Learnings

Here's what I learned from calling these tools:

1. **greet tool**: This tool provides a personalized welcome message. When called with the name "Mirascope", it returned a fun message: "Welcome to Zombo.com, Mirascope" (a reference to the quirky website).

2. **answer_ultimate_question tool**: This tool returns the answer to the famous philosophical question "What is the answer to life, the universe, and everything?" - which is **42** (a reference to Douglas Adams' "The Hitchhiker's Guide to the Galaxy"). The response includes metadata indicating this answer was computed by a supercomputer named "Deep Thought" over 7,500,000 years.

3. **process_answer tool**: This tool takes the structured ultimate answer data and formats it into a human-readable string. It takes the nested JSON structure (with information about the answer, question, and computing details) and outputs a nicely formatted message: "The answer 42 to 'What is the answer to life, the universe, and everything?' was computed by Deep Thought over 7,500,000 years"

The tools demonstrate a nice workflow where `answer_ultimate_question` generates structured data, and then `process_answer` formats that data for presentation. The greet tool adds a fun welcome element to the interaction!\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-haiku-4-5",
                    provider_model_name="claude-haiku-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
## Report on Tool Learnings

Here's what I learned from calling these tools:

1. **greet tool**: This tool provides a personalized welcome message. When called with the name "Mirascope", it returned a fun message: "Welcome to Zombo.com, Mirascope" (a reference to the quirky website).

2. **answer_ultimate_question tool**: This tool returns the answer to the famous philosophical question "What is the answer to life, the universe, and everything?" - which is **42** (a reference to Douglas Adams' "The Hitchhiker's Guide to the Galaxy"). The response includes metadata indicating this answer was computed by a supercomputer named "Deep Thought" over 7,500,000 years.

3. **process_answer tool**: This tool takes the structured ultimate answer data and formats it into a human-readable string. It takes the nested JSON structure (with information about the answer, question, and computing details) and outputs a nicely formatted message: "The answer 42 to 'What is the answer to life, the universe, and everything?' was computed by Deep Thought over 7,500,000 years"

The tools demonstrate a nice workflow where `answer_ultimate_question` generates structured data, and then `process_answer` formats that data for presentation. The greet tool adds a fun welcome element to the interaction!\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "greet",
                    "description": """\
Greet a user with very special welcome.

Args:
    name: The name of the person to greet

Returns:
    A personalized welcome message\
""",
                    "parameters": """\
{
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                },
                {
                    "name": "answer_ultimate_question",
                    "description": """\
Answer the ultimate question of life, the universe, and everything.

Returns:
    A structured answer with metadata about the computation\
""",
                    "parameters": """\
{
  "properties": {},
  "required": [],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                },
                {
                    "name": "process_answer",
                    "description": """\
Process and format an ultimate answer.

This tool demonstrates complex schema with $defs by accepting
a nested Pydantic model as input.

Args:
    answer_data: The answer data to process

Returns:
    A formatted string describing the answer\
""",
                    "parameters": """\
{
  "properties": {
    "answer_data": {
      "$ref": "#/$defs/UltimateAnswer",
      "title": "Answer Data"
    }
  },
  "required": [
    "answer_data"
  ],
  "additionalProperties": false,
  "defs": {
    "ComputerInfo": {
      "description": "Information about Deep Thought computer.",
      "properties": {
        "name": {
          "description": "The name of the computer",
          "title": "Name",
          "type": "string"
        },
        "years_computed": {
          "description": "How many years it took to compute",
          "title": "Years Computed",
          "type": "integer"
        }
      },
      "required": [
        "name",
        "years_computed"
      ],
      "title": "ComputerInfo",
      "type": "object"
    },
    "UltimateAnswer": {
      "description": "The answer to life, the universe, and everything.",
      "properties": {
        "answer": {
          "description": "The numerical answer",
          "title": "Answer",
          "type": "integer"
        },
        "question": {
          "description": "The question that was asked",
          "title": "Question",
          "type": "string"
        },
        "computed_by": {
          "$ref": "#/$defs/ComputerInfo",
          "description": "Information about the computer"
        }
      },
      "required": [
        "answer",
        "question",
        "computed_by"
      ],
      "title": "UltimateAnswer",
      "type": "object"
    }
  }
}\
""",
                    "strict": False,
                },
            ],
        }
    }
)
