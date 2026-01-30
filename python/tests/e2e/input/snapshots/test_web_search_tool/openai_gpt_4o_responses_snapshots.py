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
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 17668,
                "output_tokens": 711,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": [
                    ProviderToolUsage(name="web_search", call_count=1)
                ],
                "raw": "ResponseUsage(input_tokens=17668, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=711, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=18379)",
                "total_tokens": 18379,
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
                            text="""\
Here’s the historical Bitcoin price (BTC) on January\u202f1,\u202f2026:

• According to **StatMuse Money**, the closing price of Bitcoin on January\u202f1,\u202f2026, was **$88,722.07**. This figure is based on hourly data throughout the day, culminating in that closing value. ([statmuse.com](https://www.statmuse.com/money/ask/bitcoin-price-january-1.-2026?utm_source=openai))

• By comparison, **TipRanks** reports that on the same date Bitcoin closed at **$88,836.06**, with an opening price of $88,725.47, a high of $89,019.52, and a low of $88,323.34. ([tipranks.com](https://www.tipranks.com/cryptocurrency/btc-usd/historical-prices?utm_source=openai))

• Additional context from **Economic Times** indicates that on January\u202f1,\u202f2026, Bitcoin was trading in a relatively narrow range between **$87,500 and $88,000**, with a cited value of **$87,440** at a specific point during the day. ([m.economictimes.com](https://m.economictimes.com/markets/cryptocurrency/bitcoin-stays-range-bound-between-87500-and-88000-as-crypto-consolidation-continues/articleshow/126283114.cms?utm_source=openai))

These figures reflect slight variations depending on the data source and timestamp considered:

- **StatMuse**: closing price of **$88,722.07**. ([statmuse.com](https://www.statmuse.com/money/ask/bitcoin-price-january-1.-2026?utm_source=openai))  \n\
- **TipRanks**: closing price of **$88,836.06**, with corresponding open, high, and low values. ([tipranks.com](https://www.tipranks.com/cryptocurrency/btc-usd/historical-prices?utm_source=openai))  \n\
- **Economic Times**: trading around **$87,440** within that day’s range. ([m.economictimes.com](https://m.economictimes.com/markets/cryptocurrency/bitcoin-stays-range-bound-between-87500-and-88000-as-crypto-consolidation-continues/articleshow/126283114.cms?utm_source=openai))  \n\

To reconcile these, sources may use different exchanges for their data (e.g., Binance, Coinbase) or calculate based on different time zones or intervals. However, a reliable median estimate for the closing price lies between **$88.7k and $88.8k**.

Let me know if you'd like additional historical data, price charts, or comparisons across other dates!\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "ws_0a7994baf3e38d320069793af6cb948196814fa3f46aefa0d7",
                            "action": {
                                "query": "Bitcoin price on January 1, 2026",
                                "type": "search",
                                "queries": ["Bitcoin price on January 1, 2026"],
                                "sources": None,
                            },
                            "status": "completed",
                            "type": "web_search_call",
                        },
                        {
                            "id": "msg_0a7994baf3e38d320069793af90afc81968ccaeb6921390419",
                            "content": [
                                {
                                    "annotations": [
                                        {
                                            "end_index": 358,
                                            "start_index": 258,
                                            "title": "Bitcoin Price January 1. 2026 | StatMuse Money",
                                            "type": "url_citation",
                                            "url": "https://www.statmuse.com/money/ask/bitcoin-price-january-1.-2026?utm_source=openai",
                                        },
                                        {
                                            "end_index": 639,
                                            "start_index": 538,
                                            "title": "Bitcoin Historical Prices - TipRanks.com",
                                            "type": "url_citation",
                                            "url": "https://www.tipranks.com/cryptocurrency/btc-usd/historical-prices?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1076,
                                            "start_index": 873,
                                            "title": "Bitcoin stays range-bound between $87,500 and $88,000 as crypto consolidation continues",
                                            "type": "url_citation",
                                            "url": "https://m.economictimes.com/markets/cryptocurrency/bitcoin-stays-range-bound-between-87500-and-88000-as-crypto-consolidation-continues/articleshow/126283114.cms?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1323,
                                            "start_index": 1223,
                                            "title": "Bitcoin Price January 1. 2026 | StatMuse Money",
                                            "type": "url_citation",
                                            "url": "https://www.statmuse.com/money/ask/bitcoin-price-january-1.-2026?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1523,
                                            "start_index": 1422,
                                            "title": "Bitcoin Historical Prices - TipRanks.com",
                                            "type": "url_citation",
                                            "url": "https://www.tipranks.com/cryptocurrency/btc-usd/historical-prices?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1803,
                                            "start_index": 1600,
                                            "title": "Bitcoin stays range-bound between $87,500 and $88,000 as crypto consolidation continues",
                                            "type": "url_citation",
                                            "url": "https://m.economictimes.com/markets/cryptocurrency/bitcoin-stays-range-bound-between-87500-and-88000-as-crypto-consolidation-continues/articleshow/126283114.cms?utm_source=openai",
                                        },
                                    ],
                                    "text": """\
Here’s the historical Bitcoin price (BTC) on January\u202f1,\u202f2026:

• According to **StatMuse Money**, the closing price of Bitcoin on January\u202f1,\u202f2026, was **$88,722.07**. This figure is based on hourly data throughout the day, culminating in that closing value. ([statmuse.com](https://www.statmuse.com/money/ask/bitcoin-price-january-1.-2026?utm_source=openai))

• By comparison, **TipRanks** reports that on the same date Bitcoin closed at **$88,836.06**, with an opening price of $88,725.47, a high of $89,019.52, and a low of $88,323.34. ([tipranks.com](https://www.tipranks.com/cryptocurrency/btc-usd/historical-prices?utm_source=openai))

• Additional context from **Economic Times** indicates that on January\u202f1,\u202f2026, Bitcoin was trading in a relatively narrow range between **$87,500 and $88,000**, with a cited value of **$87,440** at a specific point during the day. ([m.economictimes.com](https://m.economictimes.com/markets/cryptocurrency/bitcoin-stays-range-bound-between-87500-and-88000-as-crypto-consolidation-continues/articleshow/126283114.cms?utm_source=openai))

These figures reflect slight variations depending on the data source and timestamp considered:

- **StatMuse**: closing price of **$88,722.07**. ([statmuse.com](https://www.statmuse.com/money/ask/bitcoin-price-january-1.-2026?utm_source=openai))  \n\
- **TipRanks**: closing price of **$88,836.06**, with corresponding open, high, and low values. ([tipranks.com](https://www.tipranks.com/cryptocurrency/btc-usd/historical-prices?utm_source=openai))  \n\
- **Economic Times**: trading around **$87,440** within that day’s range. ([m.economictimes.com](https://m.economictimes.com/markets/cryptocurrency/bitcoin-stays-range-bound-between-87500-and-88000-as-crypto-consolidation-continues/articleshow/126283114.cms?utm_source=openai))  \n\

To reconcile these, sources may use different exchanges for their data (e.g., Binance, Coinbase) or calculate based on different time zones or intervals. However, a reliable median estimate for the closing price lies between **$88.7k and $88.8k**.

Let me know if you'd like additional historical data, price charts, or comparisons across other dates!\
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
Here is the historical price of **Ethereum (ETH)** on **January 1, 2026**, according to multiple reputable sources:

• **Investing.com** reports that on January 1, 2026, Ethereum closed at **$3,004.18**, with an opening price of **$2,971.69**, a high of **$3,009.89**, and a low of **$2,971.69** ([investing.com](https://www.investing.com/crypto/ethereum/historical-data?utm_source=openai)).

• **CoinLore** provides nearly identical data: on that date, the opening was **$2,972**, the high was **$3,009**, the low was **$2,972**, and the close was **$3,004** ([coinlore.com](https://www.coinlore.com/coin/ethereum/historical-data?utm_source=openai)).

• **CoinCodex** indicates similar figures, noting a closing price of **$3,000.61**, with the high at **$3,005.04** and the low at **$2,969.94** ([coincodex.com](https://coincodex.com/crypto/ethereum/historical-data/?utm_source=openai)).

• **TipRanks** shows a slightly different closing price of **$3,018.99**, with an open of **$3,000.24**, a high of **$3,029.60**, and a low of **$2,990.88** ([tipranks.com](https://www.tipranks.com/cryptocurrency/eth-usd/historical-prices?utm_source=openai)).

• **Yahoo Finance** indicates a closing price of **$3,000.39**, with the open at **$3,006.01**, the high at **$2,966.85**, and the low value listing the close (which may reflect a formatting mix-up) ([ca.finance.yahoo.com](https://ca.finance.yahoo.com/quote/ETH-USD/history/?utm_source=openai)).

• **Exchange-Rates.org** summarizes the ETH-to-USD rate on January 1, 2026, as **$3,000.45** per 1 ETH ([exchange-rates.org](https://www.exchange-rates.org/exchange-rate-history/eth-usd-2026?utm_source=openai)).

Summary:

Across data providers, Ethereum’s price on January 1, 2026, consistently falls within the **$3,000 to $3,018** range:

- Investing.com: **$3,004.18** (closing) ([investing.com](https://www.investing.com/crypto/ethereum/historical-data?utm_source=openai))  \n\
- CoinLore: **$3,004** (closing) ([coinlore.com](https://www.coinlore.com/coin/ethereum/historical-data?utm_source=openai))  \n\
- CoinCodex: **$3,000.61** (closing) ([coincodex.com](https://coincodex.com/crypto/ethereum/historical-data/?utm_source=openai))  \n\
- TipRanks: **$3,018.99** (closing) ([tipranks.com](https://www.tipranks.com/cryptocurrency/eth-usd/historical-prices?utm_source=openai))  \n\
- Yahoo Finance: **$3,000.39** (closing) ([ca.finance.yahoo.com](https://ca.finance.yahoo.com/quote/ETH-USD/history/?utm_source=openai))  \n\
- Exchange-Rates.org: **$3,000.45** (rate) ([exchange-rates.org](https://www.exchange-rates.org/exchange-rate-history/eth-usd-2026?utm_source=openai))

If you'd like a direct comparison between this and Bitcoin’s price on the same day, or further analysis of intraday ranges or other historical dates, just let me know!\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "ws_0a7994baf3e38d320069793afcf06c8196bdd71c7b9b65e796",
                            "action": {
                                "query": "Ethereum price on January 1, 2026",
                                "type": "search",
                                "queries": ["Ethereum price on January 1, 2026"],
                                "sources": None,
                            },
                            "status": "completed",
                            "type": "web_search_call",
                        },
                        {
                            "id": "msg_0a7994baf3e38d320069793afe9ca08196b4cbad940d8d147d",
                            "content": [
                                {
                                    "annotations": [
                                        {
                                            "end_index": 390,
                                            "start_index": 296,
                                            "title": "Ethereum Historical Data - Investing.com",
                                            "type": "url_citation",
                                            "url": "https://www.investing.com/crypto/ethereum/historical-data?utm_source=openai",
                                        },
                                        {
                                            "end_index": 650,
                                            "start_index": 560,
                                            "title": "Ethereum (ETH) Historical Prices | CoinLore",
                                            "type": "url_citation",
                                            "url": "https://www.coinlore.com/coin/ethereum/historical-data?utm_source=openai",
                                        },
                                        {
                                            "end_index": 888,
                                            "start_index": 797,
                                            "title": "Ethereum (ETH) Historical Data | CoinCodex",
                                            "type": "url_citation",
                                            "url": "https://coincodex.com/crypto/ethereum/historical-data/?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1149,
                                            "start_index": 1048,
                                            "title": "Ethereum Historical Prices - TipRanks.com",
                                            "type": "url_citation",
                                            "url": "https://www.tipranks.com/cryptocurrency/eth-usd/historical-prices?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1446,
                                            "start_index": 1351,
                                            "title": "Ethereum USD (ETH-USD) Price History & Historical Data - Yahoo Finance",
                                            "type": "url_citation",
                                            "url": "https://ca.finance.yahoo.com/quote/ETH-USD/history/?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1659,
                                            "start_index": 1552,
                                            "title": "ETH to USD Exchange Rate History for 2026",
                                            "type": "url_citation",
                                            "url": "https://www.exchange-rates.org/exchange-rate-history/eth-usd-2026?utm_source=openai",
                                        },
                                        {
                                            "end_index": 1926,
                                            "start_index": 1832,
                                            "title": "Ethereum Historical Data - Investing.com",
                                            "type": "url_citation",
                                            "url": "https://www.investing.com/crypto/ethereum/historical-data?utm_source=openai",
                                        },
                                        {
                                            "end_index": 2052,
                                            "start_index": 1962,
                                            "title": "Ethereum (ETH) Historical Prices | CoinLore",
                                            "type": "url_citation",
                                            "url": "https://www.coinlore.com/coin/ethereum/historical-data?utm_source=openai",
                                        },
                                        {
                                            "end_index": 2183,
                                            "start_index": 2092,
                                            "title": "Ethereum (ETH) Historical Data | CoinCodex",
                                            "type": "url_citation",
                                            "url": "https://coincodex.com/crypto/ethereum/historical-data/?utm_source=openai",
                                        },
                                        {
                                            "end_index": 2323,
                                            "start_index": 2222,
                                            "title": "Ethereum Historical Prices - TipRanks.com",
                                            "type": "url_citation",
                                            "url": "https://www.tipranks.com/cryptocurrency/eth-usd/historical-prices?utm_source=openai",
                                        },
                                        {
                                            "end_index": 2462,
                                            "start_index": 2367,
                                            "title": "Ethereum USD (ETH-USD) Price History & Historical Data - Yahoo Finance",
                                            "type": "url_citation",
                                            "url": "https://ca.finance.yahoo.com/quote/ETH-USD/history/?utm_source=openai",
                                        },
                                        {
                                            "end_index": 2615,
                                            "start_index": 2508,
                                            "title": "ETH to USD Exchange Rate History for 2026",
                                            "type": "url_citation",
                                            "url": "https://www.exchange-rates.org/exchange-rate-history/eth-usd-2026?utm_source=openai",
                                        },
                                    ],
                                    "text": """\
Here is the historical price of **Ethereum (ETH)** on **January 1, 2026**, according to multiple reputable sources:

• **Investing.com** reports that on January 1, 2026, Ethereum closed at **$3,004.18**, with an opening price of **$2,971.69**, a high of **$3,009.89**, and a low of **$2,971.69** ([investing.com](https://www.investing.com/crypto/ethereum/historical-data?utm_source=openai)).

• **CoinLore** provides nearly identical data: on that date, the opening was **$2,972**, the high was **$3,009**, the low was **$2,972**, and the close was **$3,004** ([coinlore.com](https://www.coinlore.com/coin/ethereum/historical-data?utm_source=openai)).

• **CoinCodex** indicates similar figures, noting a closing price of **$3,000.61**, with the high at **$3,005.04** and the low at **$2,969.94** ([coincodex.com](https://coincodex.com/crypto/ethereum/historical-data/?utm_source=openai)).

• **TipRanks** shows a slightly different closing price of **$3,018.99**, with an open of **$3,000.24**, a high of **$3,029.60**, and a low of **$2,990.88** ([tipranks.com](https://www.tipranks.com/cryptocurrency/eth-usd/historical-prices?utm_source=openai)).

• **Yahoo Finance** indicates a closing price of **$3,000.39**, with the open at **$3,006.01**, the high at **$2,966.85**, and the low value listing the close (which may reflect a formatting mix-up) ([ca.finance.yahoo.com](https://ca.finance.yahoo.com/quote/ETH-USD/history/?utm_source=openai)).

• **Exchange-Rates.org** summarizes the ETH-to-USD rate on January 1, 2026, as **$3,000.45** per 1 ETH ([exchange-rates.org](https://www.exchange-rates.org/exchange-rate-history/eth-usd-2026?utm_source=openai)).

Summary:

Across data providers, Ethereum’s price on January 1, 2026, consistently falls within the **$3,000 to $3,018** range:

- Investing.com: **$3,004.18** (closing) ([investing.com](https://www.investing.com/crypto/ethereum/historical-data?utm_source=openai))  \n\
- CoinLore: **$3,004** (closing) ([coinlore.com](https://www.coinlore.com/coin/ethereum/historical-data?utm_source=openai))  \n\
- CoinCodex: **$3,000.61** (closing) ([coincodex.com](https://coincodex.com/crypto/ethereum/historical-data/?utm_source=openai))  \n\
- TipRanks: **$3,018.99** (closing) ([tipranks.com](https://www.tipranks.com/cryptocurrency/eth-usd/historical-prices?utm_source=openai))  \n\
- Yahoo Finance: **$3,000.39** (closing) ([ca.finance.yahoo.com](https://ca.finance.yahoo.com/quote/ETH-USD/history/?utm_source=openai))  \n\
- Exchange-Rates.org: **$3,000.45** (rate) ([exchange-rates.org](https://www.exchange-rates.org/exchange-rate-history/eth-usd-2026?utm_source=openai))

If you'd like a direct comparison between this and Bitcoin’s price on the same day, or further analysis of intraday ranges or other historical dates, just let me know!\
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
        }
    }
)
