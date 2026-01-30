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
                "input_tokens": 1543,
                "output_tokens": 455,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=1543, output_tokens=455, server_tool_use=None, service_tier='standard')",
                "total_tokens": 1998,
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
                            text="I'll call these tools in sequence. Let me start with the greet tool, then answer_ultimate_question, and finally process_answer."
                        ),
                        ToolCall(
                            id="toolu_01KvRYjtnLPngaWxC4QS3UyC",
                            name="greet",
                            args='{"name": "Mirascope"}',
                        ),
                        ToolCall(
                            id="toolu_01VQEnPUA6pSmD9j8ZyjMhRJ",
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
                                "text": "I'll call these tools in sequence. Let me start with the greet tool, then answer_ultimate_question, and finally process_answer.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01KvRYjtnLPngaWxC4QS3UyC",
                                "input": {"name": "Mirascope"},
                                "name": "greet",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_01VQEnPUA6pSmD9j8ZyjMhRJ",
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
                            id="toolu_01KvRYjtnLPngaWxC4QS3UyC",
                            name="greet",
                            result=[
                                {
                                    "type": "text",
                                    "text": "Welcome to Zombo.com, Mirascope",
                                    "annotations": None,
                                    "meta": None,
                                }
                            ],
                        ),
                        ToolOutput(
                            id="toolu_01VQEnPUA6pSmD9j8ZyjMhRJ",
                            name="answer_ultimate_question",
                            result=[
                                {
                                    "type": "text",
                                    "text": '{"answer":42,"question":"What is the answer to life, the universe, and everything?","computed_by":{"name":"Deep Thought","years_computed":7500000}}',
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
                            text="Great! Now let me use the process_answer tool with the data from answer_ultimate_question:"
                        ),
                        ToolCall(
                            id="toolu_015qCBwuXbQ6jwcJgM8Mz4PJ",
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
                                "text": "Great! Now let me use the process_answer tool with the data from answer_ultimate_question:",
                                "type": "text",
                            },
                            {
                                "id": "toolu_015qCBwuXbQ6jwcJgM8Mz4PJ",
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
                            id="toolu_015qCBwuXbQ6jwcJgM8Mz4PJ",
                            name="process_answer",
                            result=[
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
## Report of Tool Findings

Here's what I learned from using each tool:

### 1. **greet Tool**
- **Purpose**: Provides a personalized welcome message
- **Input**: Takes a name parameter (I used "Mirascope")
- **Output**: Returns a welcoming message: "Welcome to Zombo.com, Mirascope"
- **Observation**: Uses a whimsical reference to Zombo.com

### 2. **answer_ultimate_question Tool**
- **Purpose**: Answers the famous ultimate question about life, the universe, and everything
- **Input**: Takes no parameters
- **Output**: Returns a JSON structure containing:
  - **answer**: 42 (the iconic answer from Douglas Adams' "The Hitchhiker's Guide to the Galaxy")
  - **question**: "What is the answer to life, the universe, and everything?"
  - **computed_by**: Information about the computer that computed it:
    - **name**: "Deep Thought" (the supercomputer from the books)
    - **years_computed**: 7,500,000 years
- **Observation**: A delightful reference to science fiction literature

### 3. **process_answer Tool**
- **Purpose**: Takes structured ultimate answer data and formats it into a human-readable string
- **Input**: Accepts a nested Pydantic model (UltimateAnswer) with:
  - answer (integer)
  - question (string)
  - computed_by (ComputerInfo with name and years_computed)
- **Output**: Formats the data into a readable sentence: "The answer 42 to 'What is the answer to life, the universe, and everything?' was computed by Deep Thought over 7,500,000 years"
- **Observation**: Demonstrates how complex nested structures can be processed and converted to user-friendly output

All three tools work together nicely to greet the user, retrieve the ultimate answer, and format it for presentation!\
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
## Report of Tool Findings

Here's what I learned from using each tool:

### 1. **greet Tool**
- **Purpose**: Provides a personalized welcome message
- **Input**: Takes a name parameter (I used "Mirascope")
- **Output**: Returns a welcoming message: "Welcome to Zombo.com, Mirascope"
- **Observation**: Uses a whimsical reference to Zombo.com

### 2. **answer_ultimate_question Tool**
- **Purpose**: Answers the famous ultimate question about life, the universe, and everything
- **Input**: Takes no parameters
- **Output**: Returns a JSON structure containing:
  - **answer**: 42 (the iconic answer from Douglas Adams' "The Hitchhiker's Guide to the Galaxy")
  - **question**: "What is the answer to life, the universe, and everything?"
  - **computed_by**: Information about the computer that computed it:
    - **name**: "Deep Thought" (the supercomputer from the books)
    - **years_computed**: 7,500,000 years
- **Observation**: A delightful reference to science fiction literature

### 3. **process_answer Tool**
- **Purpose**: Takes structured ultimate answer data and formats it into a human-readable string
- **Input**: Accepts a nested Pydantic model (UltimateAnswer) with:
  - answer (integer)
  - question (string)
  - computed_by (ComputerInfo with name and years_computed)
- **Output**: Formats the data into a readable sentence: "The answer 42 to 'What is the answer to life, the universe, and everything?' was computed by Deep Thought over 7,500,000 years"
- **Observation**: Demonstrates how complex nested structures can be processed and converted to user-friendly output

All three tools work together nicely to greet the user, retrieve the ultimate answer, and format it for presentation!\
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
      "$ref": "#/$defs/UltimateAnswer"
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
          "type": "string"
        },
        "years_computed": {
          "description": "How many years it took to compute",
          "type": "integer"
        }
      },
      "required": [
        "name",
        "years_computed"
      ],
      "type": "object"
    },
    "UltimateAnswer": {
      "description": "The answer to life, the universe, and everything.",
      "properties": {
        "answer": {
          "description": "The numerical answer",
          "type": "integer"
        },
        "question": {
          "description": "The question that was asked",
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
