from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    ProviderToolUsage,
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
                "input_tokens": 89,
                "output_tokens": 584,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 380,
                "provider_tool_usage": [
                    ProviderToolUsage(name="web_search", call_count=1)
                ],
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=204 candidates_tokens_details=None prompt_token_count=89 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=89
)] thoughts_token_count=380 tool_use_prompt_token_count=165 tool_use_prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=165
)] total_token_count=838 traffic_type=None\
""",
                "total_tokens": 673,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Jan 1, 2026 is a date in the past. Use the web search tool to lookup the price of bitcoin on that date."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="On January 1, 2026, the CoinDesk Bitcoin Price Index (XBX) traded at $88,151.80 at its 4 p.m. ET level."
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "On January 1, 2026, the CoinDesk Bitcoin Price Index (XBX) traded at $88,151.80 at its 4 p.m. ET level.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="Please also look up the price of Ethereum on that date"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
On January 1, 2026, there were several predictions and observations regarding the price of Ethereum. An AI model projected Ethereum's price at approximately $3,200, with a tolerance band of about $500 on either side. Another analysis, based on the Ethereum Rainbow Chart, suggested a plausible price range of roughly $2,500 to $5,200 for that date, assuming continued gradual market expansion.

Leading up to that period, Ethereum had been consolidating near the $3,000 area. While there were reports of it dropping below $3,000 in January 2026, it was also noted that the cryptocurrency was showing signs of recovery and experiencing mixed signals from whale activity. As of January 27, 2026, the price was around $2901.62.\
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
On January 1, 2026, there were several predictions and observations regarding the price of Ethereum. An AI model projected Ethereum's price at approximately $3,200, with a tolerance band of about $500 on either side. Another analysis, based on the Ethereum Rainbow Chart, suggested a plausible price range of roughly $2,500 to $5,200 for that date, assuming continued gradual market expansion.

Leading up to that period, Ethereum had been consolidating near the $3,000 area. While there were reports of it dropping below $3,000 in January 2026, it was also noted that the cryptocurrency was showing signs of recovery and experiencing mixed signals from whale activity. As of January 27, 2026, the price was around $2901.62.\
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
            "tools": [{"name": "web_search"}],
        }
    }
)
