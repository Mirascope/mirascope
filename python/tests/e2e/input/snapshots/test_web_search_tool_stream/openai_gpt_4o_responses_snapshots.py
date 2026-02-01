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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
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
Here is what I found using reputable sources for the historical price of Bitcoin (BTC) on January\u202f1,\u202f2026:

According to StatMuse, the closing price of Bitcoin on January\u202f1,\u202f2026, was **$88,731.98**, with an opening price of **$87,508.05**, a high of **$88,803.23**, and a low of **$87,399.41** ([statmuse.com](https://www.statmuse.com/money/ask/bitcoin-price-history-janurary-2026?utm_source=openai)).

Bitcoin’s historical exchange rate data from Exchange‑Rates.org shows the Bitcoin-to-USD rate on that date as **$88,606** ([exchange-rates.org](https://www.exchange-rates.org/exchange-rate-history/btc-usd-2026?utm_source=openai)).

Additionally, Yahoo Finance’s historical data lists Bitcoin’s closing price for January\u202f1,\u202f2026, at **$88,731.98**—matching the StatMuse figure—and confirms the intraday range of **$87,399.41** (low) to **$88,803.23** (high) ([au.finance.yahoo.com](https://au.finance.yahoo.com/quote/BTC-USD/history/?utm_source=openai)).

There is some slight variation (e.g., Exchange‑Rates.org citing $88,606), which is typical given differences in data aggregation methods, exchanges, and timestamps. However:

• The most consistently corroborated closing price is **$88,731.98**.  \n\
• The intraday price ranged from approximately **$87,399** to **$88,803**.  \n\
• A reasonable midpoint estimate for the average price on that day is around **$88,600–$88,700**.

If you’d like additional detail—such as minute-by-minute data, exchange-specific quotes, or volume data—just let me know!\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "ws_0b8efb0a110fb9bc0069793b041dc88190978ddc8b0a80f2ee",
                            "action": {
                                "query": "January 1, 2026 Bitcoin price",
                                "type": "search",
                                "queries": ["January 1, 2026 Bitcoin price"],
                                "sources": None,
                            },
                            "status": "completed",
                            "type": "web_search_call",
                        },
                        {
                            "id": "msg_0b8efb0a110fb9bc0069793b0684fc819083e4cc65e29411b0",
                            "content": [
                                {
                                    "annotations": [
                                        {
                                            "end_index": 401,
                                            "start_index": 295,
                                            "title": "Bitcoin Price History Janurary 2026 | StatMuse Money",
                                            "type": "url_citation",
                                            "url": "https://www.statmuse.com/money/ask/bitcoin-price-history-janurary-2026?utm_source=openai",
                                        },
                                        {
                                            "end_index": 633,
                                            "start_index": 526,
                                            "title": "BTC to USD Exchange Rate History for 2026",
                                            "type": "url_citation",
                                            "url": "https://www.exchange-rates.org/exchange-rate-history/btc-usd-2026?utm_source=openai",
                                        },
                                        {
                                            "end_index": 956,
                                            "start_index": 861,
                                            "title": "Bitcoin USD (BTC-USD) price history and historical data – Yahoo Finance",
                                            "type": "url_citation",
                                            "url": "https://au.finance.yahoo.com/quote/BTC-USD/history/?utm_source=openai",
                                        },
                                    ],
                                    "text": """\
Here is what I found using reputable sources for the historical price of Bitcoin (BTC) on January\u202f1,\u202f2026:

According to StatMuse, the closing price of Bitcoin on January\u202f1,\u202f2026, was **$88,731.98**, with an opening price of **$87,508.05**, a high of **$88,803.23**, and a low of **$87,399.41** ([statmuse.com](https://www.statmuse.com/money/ask/bitcoin-price-history-janurary-2026?utm_source=openai)).

Bitcoin’s historical exchange rate data from Exchange‑Rates.org shows the Bitcoin-to-USD rate on that date as **$88,606** ([exchange-rates.org](https://www.exchange-rates.org/exchange-rate-history/btc-usd-2026?utm_source=openai)).

Additionally, Yahoo Finance’s historical data lists Bitcoin’s closing price for January\u202f1,\u202f2026, at **$88,731.98**—matching the StatMuse figure—and confirms the intraday range of **$87,399.41** (low) to **$88,803.23** (high) ([au.finance.yahoo.com](https://au.finance.yahoo.com/quote/BTC-USD/history/?utm_source=openai)).

There is some slight variation (e.g., Exchange‑Rates.org citing $88,606), which is typical given differences in data aggregation methods, exchanges, and timestamps. However:

• The most consistently corroborated closing price is **$88,731.98**.  \n\
• The intraday price ranged from approximately **$87,399** to **$88,803**.  \n\
• A reasonable midpoint estimate for the average price on that day is around **$88,600–$88,700**.

If you’d like additional detail—such as minute-by-minute data, exchange-specific quotes, or volume data—just let me know!\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
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
Here’s the historical price information for **Ethereum (ETH)** on **January\u202f1,\u202f2026**, based on multiple reputable sources:

• **Investing.com** reports that on January\u202f1,\u202f2026, Ethereum closed at **$3,004.18**, with an opening price of **$2,971.69**, a high of **$3,009.89**, and a low of **$2,971.69** ([investing.com](https://www.investing.com/crypto/ethereum/historical-data?utm_source=openai)).

• **CoinLore** similarly lists January\u202f1, 2026, with an open price of **$2,972**, a high of **$3,009**, a low of **$2,972**, and a close at **$3,004** ([coinlore.com](https://www.coinlore.com/coin/ethereum/historical-data?utm_source=openai)).

• **CoinCodex** gives a close price of **$3,000.61** for January\u202f1, 2026 ([coincodex.com](https://coincodex.com/crypto/ethereum/historical-data/?utm_source=openai)).

• **TipRanks** records that ETH opened at **$3,000.24**, reached a high of **$3,029.60**, a low of **$2,990.88**, and closed at **$3,018.99** on January\u202f1,\u202f2026 ([tipranks.com](https://www.tipranks.com/cryptocurrency/eth-usd/historical-prices?utm_source=openai)).

• **Yahoo Finance** shows the ETH closing price on January\u202f1, 2026, was **$3,000.39**, with an opening of **$3,006.01**, a high of **$2,966.85**, and a low of **$2,966.85** ([ca.finance.yahoo.com](https://ca.finance.yahoo.com/quote/ETH-USD/history/?utm_source=openai)).

• **Exchange‑Rates.org** indicates that the **lowest ETH–USD rate** in January 2026 occurred on January 1, with a rate of **$3,000.45** ([exchange-rates.org](https://www.exchange-rates.org/exchange-rate-history/eth-usd-2026?utm_source=openai)).

Summary (January 1, 2026 – Ethereum price estimates):

 • Closing price range: approximately **$3,000–$3,018**, with most sources clustered around **$3,000–$3,004**.  \n\
 • Opening price: generally between **$2,971.69** and **$3,006**.  \n\
 • Intraday high/low ranges vary across sources but typically fall between **$2,990** and **$3,029**.

Given the slight variations due to differing data aggregation and reporting methodologies across platforms, a reliable estimate for Ethereum's closing price on January\u202f1,\u202f2026, would be in the vicinity of **$3,000–$3,005**.

If you'd like further details such as intraday volume, specific exchange data, or minute-by-minute price movements, feel free to ask!\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "ws_0b8efb0a110fb9bc0069793b0979c88190a603b6bf292f4527",
                            "action": {
                                "query": "January 1, 2026 Ethereum price",
                                "type": "search",
                                "queries": ["January 1, 2026 Ethereum price"],
                                "sources": None,
                            },
                            "status": "completed",
                            "type": "web_search_call",
                        },
                        {
                            "id": "msg_0b8efb0a110fb9bc0069793b0b2ddc819090cfe18f60eab8ca",
                            "content": [
                                {
                                    "annotations": [
                                        {
                                            "end_index": 398,
                                            "start_index": 304,
                                            "title": "Ethereum Historical Data - Investing.com",
                                            "type": "url_citation",
                                            "url": "https://www.investing.com/crypto/ethereum/historical-data?utm_source=openai",
                                        },
                                        {
                                            "end_index": 642,
                                            "start_index": 552,
                                            "title": "Ethereum (ETH) Historical Prices | CoinLore",
                                            "type": "url_citation",
                                            "url": "https://www.coinlore.com/coin/ethereum/historical-data?utm_source=openai",
                                        },
                                        {
                                            "end_index": 809,
                                            "start_index": 718,
                                            "title": "Ethereum (ETH) Historical Data | CoinCodex",
                                            "type": "url_citation",
                                            "url": "https://coincodex.com/crypto/ethereum/historical-data/?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1074,
                                            "start_index": 973,
                                            "title": "Ethereum Historical Prices - TipRanks.com",
                                            "type": "url_citation",
                                            "url": "https://www.tipranks.com/cryptocurrency/eth-usd/historical-prices?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1345,
                                            "start_index": 1250,
                                            "title": "Ethereum USD (ETH-USD) Price History & Historical Data - Yahoo Finance",
                                            "type": "url_citation",
                                            "url": "https://ca.finance.yahoo.com/quote/ETH-USD/history/?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1591,
                                            "start_index": 1484,
                                            "title": "ETH to USD Exchange Rate History for 2026",
                                            "type": "url_citation",
                                            "url": "https://www.exchange-rates.org/exchange-rate-history/eth-usd-2026?utm_source=openai",
                                        },
                                    ],
                                    "text": """\
Here’s the historical price information for **Ethereum (ETH)** on **January\u202f1,\u202f2026**, based on multiple reputable sources:

• **Investing.com** reports that on January\u202f1,\u202f2026, Ethereum closed at **$3,004.18**, with an opening price of **$2,971.69**, a high of **$3,009.89**, and a low of **$2,971.69** ([investing.com](https://www.investing.com/crypto/ethereum/historical-data?utm_source=openai)).

• **CoinLore** similarly lists January\u202f1, 2026, with an open price of **$2,972**, a high of **$3,009**, a low of **$2,972**, and a close at **$3,004** ([coinlore.com](https://www.coinlore.com/coin/ethereum/historical-data?utm_source=openai)).

• **CoinCodex** gives a close price of **$3,000.61** for January\u202f1, 2026 ([coincodex.com](https://coincodex.com/crypto/ethereum/historical-data/?utm_source=openai)).

• **TipRanks** records that ETH opened at **$3,000.24**, reached a high of **$3,029.60**, a low of **$2,990.88**, and closed at **$3,018.99** on January\u202f1,\u202f2026 ([tipranks.com](https://www.tipranks.com/cryptocurrency/eth-usd/historical-prices?utm_source=openai)).

• **Yahoo Finance** shows the ETH closing price on January\u202f1, 2026, was **$3,000.39**, with an opening of **$3,006.01**, a high of **$2,966.85**, and a low of **$2,966.85** ([ca.finance.yahoo.com](https://ca.finance.yahoo.com/quote/ETH-USD/history/?utm_source=openai)).

• **Exchange‑Rates.org** indicates that the **lowest ETH–USD rate** in January 2026 occurred on January 1, with a rate of **$3,000.45** ([exchange-rates.org](https://www.exchange-rates.org/exchange-rate-history/eth-usd-2026?utm_source=openai)).

Summary (January 1, 2026 – Ethereum price estimates):

 • Closing price range: approximately **$3,000–$3,018**, with most sources clustered around **$3,000–$3,004**.  \n\
 • Opening price: generally between **$2,971.69** and **$3,006**.  \n\
 • Intraday high/low ranges vary across sources but typically fall between **$2,990** and **$3,029**.

Given the slight variations due to differing data aggregation and reporting methodologies across platforms, a reliable estimate for Ethereum's closing price on January\u202f1,\u202f2026, would be in the vicinity of **$3,000–$3,005**.

If you'd like further details such as intraday volume, specific exchange data, or minute-by-minute price movements, feel free to ask!\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
            ],
            "format": None,
            "tools": [{"name": "web_search"}],
            "usage": {
                "input_tokens": 17451,
                "output_tokens": 636,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": [
                    ProviderToolUsage(name="web_search", call_count=1)
                ],
                "raw": "None",
                "total_tokens": 18087,
            },
            "n_chunks": 54,
        }
    }
)
