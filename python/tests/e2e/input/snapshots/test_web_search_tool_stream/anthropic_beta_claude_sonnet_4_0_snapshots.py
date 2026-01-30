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
            "model_id": "anthropic-beta/claude-sonnet-4-0",
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
                            text="Based on the search results, I can see current Bitcoin prices and recent market movements, but I need to search more specifically for the historical price on January 1, 2026."
                        ),
                        Text(
                            text="Let me try a different search approach to find the specific historical price data for January 1, 2026."
                        ),
                        Text(
                            text="Based on the search results, I can see references to Bitcoin's end-of-year 2025 performance and early 2026 trading, but I still need to find the specific price for January 1, 2026. Let me search more specifically."
                        ),
                        Text(
                            text="""\
Based on the search results, I can see information about Bitcoin's price around January 1, 2026. Let me compile what I found:

Based on my search results, I can provide you with information about Bitcoin's price around January 1, 2026:

"""
                        ),
                        Text(
                            text="Bitcoin was trading at approximately $87,255 around New Year's Eve 2025/New Year's Day 2026"
                        ),
                        Text(text=". "),
                        Text(
                            text="Bitcoin closed 2025 trading below crucial support levels around $100k and $90k, with Bitcoin beginning 2026 after a choppy consolidation period"
                        ),
                        Text(
                            text="""\
.

More specifically, \
"""
                        ),
                        Text(
                            text="as of December 31, 2025, Bitcoin was trading at $87,696"
                        ),
                        Text(
                            text="""\
, and the search results indicate this was very close to the opening price for January 1, 2026.

The search results show that \
"""
                        ),
                        Text(
                            text="Bitcoin price closed 2025 below a crucial psychological target of $100k"
                        ),
                        Text(
                            text=", representing a significant decline from previous highs. "
                        ),
                        Text(
                            text="Bitcoin hit a 2026 low of just above $86,000 in late January, with the year's low around $87,700"
                        ),
                        Text(
                            text="""\
.

So to answer your question: **Bitcoin's price on January 1, 2026 was approximately $87,255 to $87,696**, marking the beginning of 2026 trading after Bitcoin had declined significantly from its previous highs in 2025.\
"""
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Based on the search results, I can see current Bitcoin prices and recent market movements, but I need to search more specifically for the historical price on January 1, 2026.",
                            },
                            {
                                "type": "text",
                                "text": "Let me try a different search approach to find the specific historical price data for January 1, 2026.",
                            },
                            {
                                "type": "text",
                                "text": "Based on the search results, I can see references to Bitcoin's end-of-year 2025 performance and early 2026 trading, but I still need to find the specific price for January 1, 2026. Let me search more specifically.",
                            },
                            {
                                "type": "text",
                                "text": """\
Based on the search results, I can see information about Bitcoin's price around January 1, 2026. Let me compile what I found:

Based on my search results, I can provide you with information about Bitcoin's price around January 1, 2026:

""",
                            },
                            {
                                "type": "text",
                                "text": "Bitcoin was trading at approximately $87,255 around New Year's Eve 2025/New Year's Day 2026",
                            },
                            {"type": "text", "text": ". "},
                            {
                                "type": "text",
                                "text": "Bitcoin closed 2025 trading below crucial support levels around $100k and $90k, with Bitcoin beginning 2026 after a choppy consolidation period",
                            },
                            {
                                "type": "text",
                                "text": """\
.

More specifically, \
""",
                            },
                            {
                                "type": "text",
                                "text": "as of December 31, 2025, Bitcoin was trading at $87,696",
                            },
                            {
                                "type": "text",
                                "text": """\
, and the search results indicate this was very close to the opening price for January 1, 2026.

The search results show that \
""",
                            },
                            {
                                "type": "text",
                                "text": "Bitcoin price closed 2025 below a crucial psychological target of $100k",
                            },
                            {
                                "type": "text",
                                "text": ", representing a significant decline from previous highs. ",
                            },
                            {
                                "type": "text",
                                "text": "Bitcoin hit a 2026 low of just above $86,000 in late January, with the year's low around $87,700",
                            },
                            {
                                "type": "text",
                                "text": """\
.

So to answer your question: **Bitcoin's price on January 1, 2026 was approximately $87,255 to $87,696**, marking the beginning of 2026 trading after Bitcoin had declined significantly from its previous highs in 2025.\
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
                            text="""\
Based on my search results, I can now provide you with information about Ethereum's price around January 1, 2026:

According to the search results I found, \
"""
                        ),
                        Text(
                            text="by December 31, 2025, ETH was near $2,970–$3,024, and on January 1–2, 2026, the price held above $3,000, showing a modest year-end rebound as markets opened 2026 on a balanced note"
                        ),
                        Text(
                            text="""\
.

More specifically:

- \
"""
                        ),
                        Text(
                            text="Ethereum opened around $3,354 on 1 January, fell to close near $2,488 by 30 June, and then re-accelerated to end the year at about $2,968 on 31 December, before moving above $3,100 in early January 2026"
                        ),
                        Text(
                            text="""\

- \
"""
                        ),
                        Text(
                            text="Ethereum price reclaimed $3,100 as 2026 trading opened with bullish momentum"
                        ),
                        Text(
                            text="""\


So to answer your question: **Ethereum's price on January 1, 2026 was approximately $3,000 to $3,100**, specifically opening the year around the $3,000 level and quickly climbing above $3,100 in the first few days of January 2026.

This represented a recovery from the December 31, 2025 closing price of approximately $2,968, showing \
"""
                        ),
                        Text(
                            text="Ethereum price as the year 2026 begins has rallied past $3,100, marking a strong recovery. The 5% gain pushed ETH to $3,122, its highest level in weeks"
                        ),
                        Text(
                            text="""\
.

The price movement coincided with \
"""
                        ),
                        Text(
                            text="the release of a new scaling roadmap by Ethereum co-founder Vitalik Buterin with a 2026 target"
                        ),
                        Text(text=", which helped drive early 2026 momentum."),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Based on my search results, I can now provide you with information about Ethereum's price around January 1, 2026:

According to the search results I found, \
""",
                            },
                            {
                                "type": "text",
                                "text": "by December 31, 2025, ETH was near $2,970–$3,024, and on January 1–2, 2026, the price held above $3,000, showing a modest year-end rebound as markets opened 2026 on a balanced note",
                            },
                            {
                                "type": "text",
                                "text": """\
.

More specifically:

- \
""",
                            },
                            {
                                "type": "text",
                                "text": "Ethereum opened around $3,354 on 1 January, fell to close near $2,488 by 30 June, and then re-accelerated to end the year at about $2,968 on 31 December, before moving above $3,100 in early January 2026",
                            },
                            {
                                "type": "text",
                                "text": """\

- \
""",
                            },
                            {
                                "type": "text",
                                "text": "Ethereum price reclaimed $3,100 as 2026 trading opened with bullish momentum",
                            },
                            {
                                "type": "text",
                                "text": """\


So to answer your question: **Ethereum's price on January 1, 2026 was approximately $3,000 to $3,100**, specifically opening the year around the $3,000 level and quickly climbing above $3,100 in the first few days of January 2026.

This represented a recovery from the December 31, 2025 closing price of approximately $2,968, showing \
""",
                            },
                            {
                                "type": "text",
                                "text": "Ethereum price as the year 2026 begins has rallied past $3,100, marking a strong recovery. The 5% gain pushed ETH to $3,122, its highest level in weeks",
                            },
                            {
                                "type": "text",
                                "text": """\
.

The price movement coincided with \
""",
                            },
                            {
                                "type": "text",
                                "text": "the release of a new scaling roadmap by Ethereum co-founder Vitalik Buterin with a 2026 target",
                            },
                            {
                                "type": "text",
                                "text": ", which helped drive early 2026 momentum.",
                            },
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [{"name": "web_search"}],
            "usage": {
                "input_tokens": 17,
                "output_tokens": 594,
                "cache_read_tokens": 16392,
                "cache_write_tokens": 24164,
                "reasoning_tokens": 0,
                "provider_tool_usage": [
                    ProviderToolUsage(name="web_search", call_count=2)
                ],
                "raw": "None",
                "total_tokens": 611,
            },
            "n_chunks": 184,
        }
    }
)
