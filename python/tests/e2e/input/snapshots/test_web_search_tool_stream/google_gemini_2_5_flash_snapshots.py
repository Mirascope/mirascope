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
            "finish_reason": None,
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
                            text="On January 1, 2026, the price of Bitcoin traded at $88,151.80."
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
                                "text": "On January 1, 2026, the price of Bitcoin traded at $88,151.80.",
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
While an exact price for Ethereum on January 1, 2026, is not definitively stated in the search results as a single, confirmed value, several sources provide insights into its price around that date.

According to a Finbold article from December 15, 2025, the Ethereum Rainbow Chart suggested a plausible price range for January 1, 2026, of roughly $2,500 to $5,200. Another article from January 27, 2026, mentions that Ether had been consolidating near the $3000 area earlier in January. Binance also reported on January 25, 2026, that despite a price drop of over 10% in the past week and a decline below $3,000, Ethereum's network activity had reached an all-time high. Additionally, a key support level was identified at $2,850 in a January 22, 2026, analysis.\
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
                                "text": "While an",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": " exact price for Ethereum on January 1, 2026, is",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
 not definitively stated in the search results as a single, confirmed value, several sources provide insights into its price around that date.

According to a Finbold article from December 15, 2025, the Ethereum Rainbow Chart suggested\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": " a plausible price range for January 1, 2026, of roughly $2,500 to $5,200. Another article from January 27, 2026, mentions",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": " that Ether had been consolidating near the $3000 area earlier in January. Binance also reported on January 25, 2026, that despite a price drop of over 10% in the past",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": " week and a decline below $3,000, Ethereum's network activity had reached an all-time high. Additionally, a key support level was identified at $2,850 in a January 2",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "2, 2026, analysis.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": None,
            "tools": [{"name": "web_search"}],
            "usage": {
                "input_tokens": 73,
                "output_tokens": 237,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 33,
                "provider_tool_usage": [
                    ProviderToolUsage(name="web_search", call_count=1)
                ],
                "raw": "None",
                "total_tokens": 310,
            },
            "n_chunks": 9,
        }
    }
)
