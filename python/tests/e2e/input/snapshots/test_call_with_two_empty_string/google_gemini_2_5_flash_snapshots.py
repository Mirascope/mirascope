from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 1,
                "output_tokens": 535,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 368,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=167 candidates_tokens_details=None prompt_token_count=1 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=1
)] thoughts_token_count=368 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=536 traffic_type=None\
""",
                "total_tokens": 536,
            },
            "messages": [
                UserMessage(content=[Text(text=""), Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Many things can be seen in the sky at night! Here are some of the most common answers:

1.  **Stars**
2.  **Moon**
3.  **Planets** (like Venus, Mars, Jupiter, Saturn)
4.  **Clouds**
5.  **Constellations** (patterns of stars)
6.  **Meteors** (shooting stars)
7.  **Satellites** (artificial, like the International Space Station or other spacecraft)
8.  **Aircraft/Planes** (with their lights)
9.  **Comets** (less common, but can be visible)
10. **Aurora Borealis/Australis** (Northern/Southern Lights, in polar regions)

What were you thinking of?\
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
Many things can be seen in the sky at night! Here are some of the most common answers:

1.  **Stars**
2.  **Moon**
3.  **Planets** (like Venus, Mars, Jupiter, Saturn)
4.  **Clouds**
5.  **Constellations** (patterns of stars)
6.  **Meteors** (shooting stars)
7.  **Satellites** (artificial, like the International Space Station or other spacecraft)
8.  **Aircraft/Planes** (with their lights)
9.  **Comets** (less common, but can be visible)
10. **Aurora Borealis/Australis** (Northern/Southern Lights, in polar regions)

What were you thinking of?\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
