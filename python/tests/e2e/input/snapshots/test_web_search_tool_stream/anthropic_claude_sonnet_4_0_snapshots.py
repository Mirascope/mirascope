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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
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
                            text="""\
I was unable to find the specific Bitcoin price for January 1, 2026 in these search results. The results show current Bitcoin prices (around $87,000-$88,000 as of late January 2026) and discuss recent market movements, but don't provide the historical price data for New Year's Day.

Let me search more specifically for historical Bitcoin price data for that exact date.\
"""
                        ),
                        Text(
                            text="""\
Based on the search results, I found some information about Bitcoin's price around January 1, 2026:

"""
                        ),
                        Text(
                            text="The price briefly touched an intraday high of $94,352 after opening the year near $87,400 on Jan. 1"
                        ),
                        Text(
                            text="""\
, according to Bitcoin Magazine Pro data.

Additionally, another source indicates that \
"""
                        ),
                        Text(
                            text="The flagship coin dropped over 1% in the past 24 hours to trade at about $87,255 at press time"
                        ),
                        Text(text=" around New Year's Eve, and "),
                        Text(
                            text="The price of Bitcoin (BTC) has declined by 0.41% over the last 24 hours"
                        ),
                        Text(
                            text="""\
 on January 1, 2026.

So based on the available data, **Bitcoin opened 2026 near $87,400 on January 1, 2026**, and during the day it reached an intraday high of $94,352. The price showed some volatility around the New Year period, with reports of it trading around $87,255 on New Year's Eve and experiencing minor declines of around 0.41% to 1% in the 24-hour period around January 1st.\
"""
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
I was unable to find the specific Bitcoin price for January 1, 2026 in these search results. The results show current Bitcoin prices (around $87,000-$88,000 as of late January 2026) and discuss recent market movements, but don't provide the historical price data for New Year's Day.

Let me search more specifically for historical Bitcoin price data for that exact date.\
""",
                            },
                            {
                                "type": "text",
                                "text": """\
Based on the search results, I found some information about Bitcoin's price around January 1, 2026:

""",
                            },
                            {
                                "type": "text",
                                "text": "The price briefly touched an intraday high of $94,352 after opening the year near $87,400 on Jan. 1",
                            },
                            {
                                "type": "text",
                                "text": """\
, according to Bitcoin Magazine Pro data.

Additionally, another source indicates that \
""",
                            },
                            {
                                "type": "text",
                                "text": "The flagship coin dropped over 1% in the past 24 hours to trade at about $87,255 at press time",
                            },
                            {"type": "text", "text": " around New Year's Eve, and "},
                            {
                                "type": "text",
                                "text": "The price of Bitcoin (BTC) has declined by 0.41% over the last 24 hours",
                            },
                            {
                                "type": "text",
                                "text": """\
 on January 1, 2026.

So based on the available data, **Bitcoin opened 2026 near $87,400 on January 1, 2026**, and during the day it reached an intraday high of $94,352. The price showed some volatility around the New Year period, with reports of it trading around $87,255 on New Year's Eve and experiencing minor declines of around 0.41% to 1% in the 24-hour period around January 1st.\
""",
                            },
                        ],
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
                            text="Let me search more specifically for Ethereum's historical price data around January 1, 2026."
                        ),
                        Text(
                            text="""\
Based on the search results, I found specific information about Ethereum's price around January 1, 2026:

"""
                        ),
                        Text(
                            text="By December 31, 2025, ETH was near $2,970–$3,024, and on January 1–2, 2026, the price held above $3,000, showing a modest year-end rebound as markets opened 2026 on a balanced note."
                        ),
                        Text(
                            text="""\


Additionally, other sources provide more context about Ethereum's price movement around that period:

"""
                        ),
                        Text(
                            text="Ethereum opened around $3,354 on 1 January 2025, fell to close near $2,488 by 30 June, and then re-accelerated to end the year at about $2,968 on 31 December, before moving above $3,100 in early January 2026."
                        ),
                        Text(
                            text="""\


So to summarize both cryptocurrencies' prices on January 1, 2026:

- **Bitcoin**: Opened near $87,400 and reached an intraday high of $94,352
- **Ethereum**: Was in the range of $2,970–$3,024 at year-end 2025 and held above $3,000 on January 1-2, 2026, before moving above $3,100 in early January

Both cryptocurrencies showed some strength entering 2026, with Bitcoin experiencing more dramatic intraday volatility and Ethereum showing a steadier recovery above key psychological levels.\
"""
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Let me search more specifically for Ethereum's historical price data around January 1, 2026.",
                            },
                            {
                                "type": "text",
                                "text": """\
Based on the search results, I found specific information about Ethereum's price around January 1, 2026:

""",
                            },
                            {
                                "type": "text",
                                "text": "By December 31, 2025, ETH was near $2,970–$3,024, and on January 1–2, 2026, the price held above $3,000, showing a modest year-end rebound as markets opened 2026 on a balanced note.",
                            },
                            {
                                "type": "text",
                                "text": """\


Additionally, other sources provide more context about Ethereum's price movement around that period:

""",
                            },
                            {
                                "type": "text",
                                "text": "Ethereum opened around $3,354 on 1 January 2025, fell to close near $2,488 by 30 June, and then re-accelerated to end the year at about $2,968 on 31 December, before moving above $3,100 in early January 2026.",
                            },
                            {
                                "type": "text",
                                "text": """\


So to summarize both cryptocurrencies' prices on January 1, 2026:

- **Bitcoin**: Opened near $87,400 and reached an intraday high of $94,352
- **Ethereum**: Was in the range of $2,970–$3,024 at year-end 2025 and held above $3,000 on January 1-2, 2026, before moving above $3,100 in early January

Both cryptocurrencies showed some strength entering 2026, with Bitcoin experiencing more dramatic intraday volatility and Ethereum showing a steadier recovery above key psychological levels.\
""",
                            },
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [{"name": "web_search"}],
            "usage": {
                "input_tokens": 17,
                "output_tokens": 515,
                "cache_read_tokens": 16242,
                "cache_write_tokens": 23258,
                "reasoning_tokens": 0,
                "provider_tool_usage": [
                    ProviderToolUsage(name="web_search", call_count=2)
                ],
                "raw": "None",
                "total_tokens": 532,
            },
            "n_chunks": 148,
        }
    }
)
