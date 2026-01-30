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
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 76636,
                "output_tokens": 606,
                "cache_read_tokens": 64992,
                "cache_write_tokens": 11627,
                "reasoning_tokens": 0,
                "provider_tool_usage": [
                    ProviderToolUsage(name="web_search", call_count=2)
                ],
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=366), cache_creation_input_tokens=11627, cache_read_input_tokens=64992, input_tokens=17, output_tokens=606, server_tool_use=ServerToolUsage(web_search_requests=2), service_tier='standard')",
                "total_tokens": 77242,
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
                            text="Let me search more specifically for Bitcoin's price on January 1, 2026:"
                        ),
                        Text(text="Let me try another search approach:"),
                        Text(
                            text="""\
Based on the search results, I can provide you with information about Bitcoin's price on January 1, 2026:

"""
                        ),
                        Text(
                            text="The price briefly touched an intraday high of $94,352 after opening the year near $87,400 on Jan. 1"
                        ),
                        Text(
                            text="""\
, according to Bitcoin Magazine Pro data. This indicates that Bitcoin opened the year 2026 at approximately $87,400.

Additional context from the search results shows that \
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

The search results also indicate that \
"""
                        ),
                        Text(
                            text="Bitcoin (BTC) price has closed 2025 trading below crucial support levels around $100k and 90k"
                        ),
                        Text(text=" and that "),
                        Text(
                            text="After closing 2025 in a choppy consolidation, Bitcoin will begin 2026 on a high bullish note"
                        ),
                        Text(
                            text="""\
.

So to summarize: **Bitcoin's price on January 1, 2026 opened near $87,400 and reached an intraday high of $94,352**.\
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
                                "id": "srvtoolu_01L3JVYNa5X5schrHemWyp2J",
                                "input": {"query": "bitcoin price January 1 2026"},
                                "name": "web_search",
                                "type": "server_tool_use",
                            },
                            {
                                "content": [
                                    {
                                        "encrypted_content": "EqEDCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDMQNnXhWVwdK8OA8VxoMG+cXf5VQTPWqLxs6IjCIi7o82quueFx/N/XJSH9QEFQRqeCGE3GjbbCoCRxIZSL79VHssAzmvpllYBV07oQqpALSvOmfgvfHQT+ZWDMoSpwJeVTZD2N+ncxnYctQf8b0P6PqpwCVOYCpkloNdNpQIgFF4F3uxFhrrpLvO/qJvD1t0QLDudilmL6vZHwwEYqQr1RBOM9aJeP4j5I/CW1tPP3BgKWHnQx5iTdgigSMt5Zn2MzftHJ0lhr3SWbNEZyeD5lLlxgZaHFGp5Zajc8h5C5NJSWlC9twPdtrdpy+Ya2fw1cRuAAYrLOQUYykSb/e2mOLjdAPcKyMswPonYoAWZ5CAdC8/o9ILS4mkM1JpGa3jNo2UozU7FjjalEkRZBDnzGSzl+Q9XDSMwiFNFrQdz71Wr/Xpxbz/HYQVd6m+AFWR6oQAiLESMNCi8p01N+c9Eg9rFKB9012ZaTV6dSclDOf/lmFGAM=",
                                        "page_age": None,
                                        "title": "Bitcoin USD (BTC-USD) Price History & Historical Data - Yahoo Finance",
                                        "type": "web_search_result",
                                        "url": "https://finance.yahoo.com/quote/BTC-USD/history/",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "1 day ago",
                                        "title": "Key BTC price levels to watch as downtrend pressure builds",
                                        "type": "web_search_result",
                                        "url": "https://www.coindesk.com/markets/2026/01/26/key-bitcoin-price-levels-to-watch-as-downward-pressure-builds",
                                    },
                                    {
                                        "encrypted_content": "Eq8CCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDMn253m8z1wtQTjjzBoM/a/uZyxaz5clj0oAIjBVRWf4HSWmNOA5ZZCfgY+pNhPeJe36VmNB62TjbSLDQBrBD1KW5ErQ5jVhbFQyDBkqsgF2IdA8cFcCtW/c+ycsuYQeCv5OzlLlLjy8mCBR5+5N7CMVzKI6z2Tf7BFon2DGvkAH5xsHeEUuKjckqh12i71zFoqIQPqgduyCb5sJJ0ol/2r1/yFCICNC5r9T57cUx/GQ7t3v73OVCjZNTGyjl/QfT8ocVLTp3NyLtpqwkQTpqUFblC1pPwHrQ2RIvQIQih9/5/xsvSXO2c4Jx+JWMnYDCLjsxmNSpqEU+o0KmzGdY0KkGAM=",
                                        "page_age": None,
                                        "title": "HISTORICAL BITCOIN PRICES ON JANUARY 1 🎉🥂 2026",
                                        "type": "web_search_result",
                                        "url": "https://www.binance.com/en/square/post/34505018894106",
                                    },
                                    {
                                        "encrypted_content": "EqACCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDDdNwFzhYj+qJyYTcxoMw88wEe0/80SnFb0MIjCUHzBa4l88fhf1l94cyROTFP+0xbw+fwMGEQAXC/TpnxvbNuQ7WMjsnRkDcRXtcdQqowF3GwoB0e0JqAjHaWR+tZxd8TdBNXk9fdNfvDBmLWV4hoSCw/6kpmisWpw9mrFUWNJ9NaL/ffsyoxusK304+cal8mKOwZR6R7uNz0jyVCqNPtHztucnVDyKIT3jZ9iF1gw785Kp4z+ezG9M7aWMS1bIh+GJPGbFi98e9i0E3DFWWGi2L+UldQFQ9l6TraRCeZaR4Dyar/VOv4xpEDjaEihpc9WfGAM=",
                                        "page_age": None,
                                        "title": "BTC Price News: Bitcoin rises to key level while analyst sets $100,000 target",
                                        "type": "web_search_result",
                                        "url": "https://www.coindesk.com/markets/2026/01/13/bitcoin-rises-2-to-usd93-500-after-inflation-data-increased-chances-of-further-rate-cuts",
                                    },
                                    {
                                        "encrypted_content": "EoMCCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDLWXcanrPQFIcFcGdhoMKy9Mr0OLhT/12ttmIjChA5KWmwjaU3Gr5MIiV9A6qTJ9mh1PFJDO8XPDLd6VjXeeOakAIOL7xNfQtxjIqtEqhgGOUX3jt9xKWqDbg06ndCAF7bprXmgQQ/6O70FBnk6a1It6FO+et33dobFZ9/AqpJTN4zH3I4f96dzhd7cVLLHFNhzUlhfqaHbOfSZTzPq22cvLEBcUEJIqQoS4jFjBYspHFl9YK3p2ADRmdXDv5pEmFmUu36r1l8Mhz/3rMyfN0FboemSEbhgD",
                                        "page_age": None,
                                        "title": "How high will Bitcoin get this year? Odds & Predictions 2026",
                                        "type": "web_search_result",
                                        "url": "https://kalshi.com/markets/kxbtcmaxy/how-high-will-bitcoin-get-this-year/kxbtcmaxy-26dec31",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": None,
                                        "title": "Bitcoin Price History and Historical Data | CoinMarketCap",
                                        "type": "web_search_result",
                                        "url": "https://coinmarketcap.com/currencies/bitcoin/historical-data/",
                                    },
                                    {
                                        "encrypted_content": "EpQgCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDCROHFTlRfA2xr+DEhoMG4WooHZYR06e2zsAIjB2NAe6lFy7DSz3EpXJz2YiDN7O80oaYmVsOYo3XURvFJUgO3siik5M/Wz/TjqbVycqlx8P+8oMWAALLIwP+QktyJUmLFjBEQp05B6s7m+0Yk2St5MJpITjp22KNlPVDea2roywmPKyNmvnr/ghuOBxjF//p4lJI38Ld0HdbYRFmzYjnE/F//A5bsRzKrJFXZXUe5kTg04Z/+sfZqktHvJLlGMMsxhXObOqKIrQsAkdTm0zkryS6Bh65C51Dx+nRLUORcP7GnItpcIMGNlmpoLGoy1lN/g/XOr5QaxNLihi8Yr26v9kW5GD5KlVzDm7N2RA/C3PCCQ3soF9ALrubE1zIWdzECX06YsqzSPhuXScqmWO7CrbCX95K4CZALEL/swxevVzgfcOICKfD52lgZ7Iotx7r1U46FLYexFV7KzNUQZLAaNAOs0uaJDjuU25EuUuMvMOvRbnZYLNnTBknbq4FgQlBsF+dp8LuoZmWSot0DzgtyaVxBGZdnkBCv70/ADNa50w/MA982bvB+4EfwrPl/oDfzQD+YszmOrXjQrRMVQSF/aUpvZ0wdU7WQcNCcksKrgAlBiAm+oISe9uEfLbS8D9LbktgP4u3lgCZ6pEnr6tboXZ//iBTgchhPpPH1Imoq0GPP7Ds1srPl78L+o+zMVTHxfhYE3iOm8bzIMTm0QXHnKFBHLngsAOnvBaOhsfCqbTLZ9/Xy7OUSWbZraR3bKhrN30QH4YeveBR1xW8vlBUGT2oTBqCW+LkDbI9udrR3JAGRqFTnTc9/uZUGfA9LYnLZxEJKEmKqdozwo1ZeLFIqysqq4DeUMLYlmlk6tF7Fu4e0XV9l/swKgkuUpXuHqQnZJWGJ/NQuol+SulNs4q5hwmsSB36cDKaIIsn0KOrlx0nsG1Vc0PhA0lajOwfKq+kfAr5Ks1bCGgZSPMdys6R0o3NUaytQTCiBtg4U5kRhNjtz6NQRNBMp8At7NRgKIFJUucpQ/KMk3PtZGasNTFaA3Q+4Cs/hrckKurzeacVe554ZwrRDu1aOg4i+G6aJssvmIAFY4n2ybQJKlpLUCCVgS2xA0Gwj+Dv2wxDnYXrIyt9uV/w/bnEwpB31anh8jlN1SdIHu7VGsT+2KvYGdUWhzcdo0E8kk+Y/k20soSjcSLTa4wcMscN07HEUsD6ojpw6XrBjBVabiRFI+8XG6KVTaAateNNC4a/juMlmGIpcVIt+/OPfQzP5mgxdh0sr93tS70slZQxZF+h1tyONwnOSXmsoiyNXUESaQ748QIrGjt5aNPnIRzaPWPotJ7kRA3HiQK3lN4VcaZkMgH5pKmDv6E63cg0DdmYkCbBomCoKNkkXA9Klr6HCdUh3tJLXWC7ec9/w/s+7K3Oyv8S8NOvGU0jUCtiKmx9gMakw7afd8BSr6ZkICZeO5tpfTZiaY0TpHITyQT0pDAFwH8v1rXcfrVDc+BkHHxCoLzpAM8k+KF2kFQr8RUt5eS6711qpNw0uS1/rQ9Q4Tj4YKob7vMunp1B+0MzxC4iG4NLgp2b5sPKwKrA+We9BILaSVU9/PHvnD2nMf3U85IMUJc74mW4eii2r6MLLQi06JOtAZiTTVQZ/ZIf9Hv3CxJXRP+xg94O/Es+ZJKGToTsTrGyvTGSiVfWpTWjfCdMEv2gB8DyN5RHOKS591HBgKcG3rl41S+tkNnso3xcHLzaPX63sBFgKR5ECCQqUjFX+qerf9+hgNKNKiSf6H1i6ZPZHo4D5XBVysoQ4xCmjzW3uFhn1cL8GLtZKVbstwHb6F2NIlVhsBSErx7Y+AhBldTEzGJLMTu6/oXIPLNolUq/Bz2wx9qNJ+cnohRF/G7DR8Y65+c1awQ0ejnUSgO40IRv5PgVPB1ME5pa7Z0nhjlr3vPGJ8okUYuDaYshyMPcSFSWfny+7r8fRl5JC8GOpxJgua06oMfOFMTntYpNqr3f8RbemtKm29BmjN07tfjBWLzaUCsyqbG8z7bSbEUcdlmbS9Pt0Rg7qlqn/OWIxQBveqWLNTYL0AUg+yc6BQ8Bru+1wVFkID25Xh2Ngrcz0u8DFf+FmD0LXWZNPf9zPAu6GMihxapTAHS1hRWGoTbyWGT8Y74tTUREI349U1p39pZgzzKwhwozxzLd2Gijv3kFhPHPcUhrlHDkn0YPuSvPIEUXbnI9nz8WUuWEuOkbIZQd6k0FdN+t+m4KZQmBjhrlFZN2po6iNmGv0FiGwPSHH8CA7GXhTbW1dBhTgGqtQ3Eq2WphU6mrLHUc1SGmgu8FPg9ASHb/98J702w9q5SEDWCfP1vsYpgj0nxDrP2j7+txHKf8EQXs7ONqf3QG36qHVPbfKb0hp/a6vmkRN3mAla9zCsMg4IKp1BvfAfBbztxZ1GGLqEQfDvMlbpl5skA3SUty/X5AtBPrE3FBGlJW2coavQpE0T1CHzu1RUbvzPCvvJPEmTv2X/pEmMECatUaint5pdyku4rVOgCVZV2T/lS9CjlU/4OJF5mK+2K1y9CPEEtBVEyEmKysx9OGce8isZLoHsCA13oejnEWeJQLmv4kqKY4mMtmsV+b5m64VyywH8+UnBHyU/YqECvbLhPl1EcPV6xKwgtGdH39VTXd30MZlWxUx5suEuTmwN/sT/qSa697tN1ToByUiLDGUwUE1UzgPGt4axghm+IgvlJjKl374LfoDbi5WNPHw7EuJkZixWiXgDMOHCg/7D9qJA1+SfZ8MUkOOmDIt2dC+TRHBWIVL5lgFlu4ZpqGcYKUbLXug+b0DDgNpFNdPwT88M4iV7bW7TbnjVjXZuZCCsQq1oBy4saMJLySC+6Ctc1Ap8E5Cttk36/TpWB8fHnyrbUVeq4PuzqS6KXR/nz3JN9mQsE5SOxvgOeESvh2qrJrXZu/gFIDEsaSgi7W/mLpx3a4d4yGv55ckmIDmayzL0qJNunoa2EhgPB8qb6oTCDD+8pPVXrcxFhQ9zyfC3ojKOYE0JjHxgHntzGa60Q5P1HMWCUE+17rbLbUr9bkqiqOzOGM7v+V3b/DLJC65Kp4ARkgJjCJVAKpsk1u6tg4UkeRiJtvP08XAeXFE3HlmxhtGTykcLIDnAlEKlEsNpOPGLTSG77/sf6qNdC3ZHS4+4M+VPDD3VSrMLP10bKC3a2/NjVIXFoL7Ucj2hBMFOJ61C0VyvTGGFpd2CR0lbhw+rm7FOgy6TMh23JwLzL7j3OqVQCCbD2i40x4gRWmUFtJzN38gGfb65Ye/XJBlcC5USevbG/5ob8iBK2xhQ7Sgxow8Pg1s+lGEbisDDNVLq7OGaATGiFqqkGiYdmG332JbyeQdySssHaaJWvnjSUUtcbRVsWsG3CU3TeuLCY9QiyosbWRJpXEBzi1qSyY3p8JUAm9SerGvkIt34/P0+suQQbreZpstjXrYrXhbk2QlPy7hdGTAbPM2Ld8nZmyXcMPa6dMMuXOR41r9K3qBLhVREcj/0xFz7SHfHRX86vBIo9zekWgVLkxgxrwJSSY9GNyM2O3EtoE7jrnt5vSXk84p5+EvwGz+FB0A59Va3iGwHNs1QSPNrJ92opT8hinaEmUTG2nCxYswJ4osIbrNr4dwfbpMmPSoum4AmGC/soFhF2/45gdDeSv50JgkeUcmkD2zBBtaTbnB3NBnB5upnkeqfztKhQ19yrK99ZUehtULgmm2QJv8xbBl1WQo/UE4hNvhsiNwkFYhcDN1Bcc1q9i9K5hOVmwNbKCVqkxGhDGf0Ls42n5zSPyN4OxFVcik4LmKJwpi/JFwZ6lNKyDS0zVZhW8Io2op8E9XI9bQliGbuDte91raJL4cVrqqT042tj6ePWdSCE6uf4IP5nSIBQiu3U4e03UeLleGBUcD8BVEcN/ZuMijUP0p/E9aOy7uavHFBIIiM1ag5gBik3JnDQEnP4xWCh+I/61yFZoGZEcT0mCqKjS0hHPHpPS2z8eLbuLuyGdqgO3br8Rh8x+/ul7c3hSL0kZHrD7RwSrtBHtDeB6kRuVt99tR0hTLrIewiuIY/NzhXul8jCARx7mzZaQnfMGQDkMUXJs8FrXwiCOftzX1j9EixZlyCWQoy/CmdOJ5HO8O8YT9r4dd6VYJWHkfIdjBHIVz9fAGb84pwCKTsPDtUcWk4DFcy3eOd5DiDhFXA4GAWis6aZuyxX9HryBmqG7gTZyC9jknFfv4//Rh6bDpQOa3yROfYeHj0WLabcZmYGFF7YphLCamw+h/YDUErRhqXVmW1Cq5hWAZw/yVXEJpKqZalW9DMk08XD5+tEEr/6p57/Z9bCwbPnRmrlyUjpHc3+6lBtvzB/UFTtbXswHkNk85BOA+ATidymnJVrUlT5wUnE6R2zvAnpLFFC3X21EzyzV8x+x95xDLInDBSLMRHSwmn3RGM1cezNBtfzD4UqAgYDHye8xL1Z/1Ue476JOCM9ZYOlQ97O76Jjtz/0XgZGF0Vhq4XGyv2zE7v2LAYMDp0Whs5r9nNE1AL7IdM0imiDW5aa+ycRRPjInT2zChHJd+/pqfs27N6AUBHl78k+F8mjqR7hJeJABngqaWiL7XipSFg7elQl/CI6ejZ4d2bOdf9vOZTUwr5ke3DgO+hg95EhITNrUxC8bcuro9JtXXAfZsOsyO28xXZ9EVP2r5JtmuFIROaN3MqE6KynzeG5Gw8Y1yQhJxi5Knt7g76jp9KQEoXRBlZNoq5g6rG6pO2uuW+j5MsYXOLyNIvsFvGEHCfBmXgDMtKj3qUAvfrw7CeWaNT92iqnsqVFL1A9nV712KlYjA7Xbhd0p9kGwtf9p6gY0205o5aTdsd4Ihrxv7fsYGHXnFI+lp9ivLY3n1IdditlOt7tbWar/5b035vwcRJAnVa/gE846l2vnXglbM0bwmqOt1Y0fEb/Q4cxwyjr5v4lvI2UpuP4Giuu3zdYPjQrlrX4QmrfMsu4jogpn96zNWW/DB0V0r/kTyXKVRqScJQFge3rWw0hegYSxAg+5O7ZKuMqq74yWWnEBZ/6kxnmvgdRfdN9Lmw9HlOrVLbr1JDs8bwqQZhWeS8+q4eT2V8eEQMGlfrT2lcnoC5D2Sb9M4Ie9OdtuA2ujKbJlD8DRVpQgnfZXZZ2ryogaQpOHBd8zoPb27ZvCx5awozae0gQ7WB2kolQNpUEqTDwnC3Jr/IB3K2R9TpOZKL8/gxwKfVgTyq3aVGwdvgACXSmcjWrIM2CejFzq8GbeAu8Db6pIVEF/IyG7pDtsTWkG12HCpoY2IpFjP85Onl08Zx38bVU5nfjmN0SQWlICIGf8l/YZpXrXnNgEcC3Ac/1oOm24C9fmf0WlKYGnyo9P+gwbImaiDoCL6hFpOKHbXX709HY5zsOg99a+NzKLEgsqE1fFet/gWW2gLUpkaXf/2S2GAM=",
                                        "page_age": "1 day ago",
                                        "title": "Bitcoin price news: BTC holds near year's low as precious metals continue garnering attention",
                                        "type": "web_search_result",
                                        "url": "https://www.coindesk.com/markets/2026/01/26/bitcoin-stuck-near-usd88-000-as-gold-s-and-silver-s-record-breaking-rallies-show-exhaustion-signs",
                                    },
                                    {
                                        "encrypted_content": "EpUGCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDIQJd1LdlZvwLWfLVRoMTtj5iO1hc5g4s9o7IjAfiq8gY3PSBVk+EXGci2gyCIf/TjG7vyaL/PJqc2i8jNcasAOdYjS5t309/vWyCh0qmAVYnXrH4G6Mq52MamRX5xUDVX2suc7mt75Z9i1h5lfizZZ1B68h6g60HR/o+lUK0UrkCsV0PuOtf2Y5KgoMYxaetuP+0lq001IGTGvQpUgeQEJ1bZQ/2IRp6Su/aYuD0RCOM4uwceALOClyX45VIk8Z8VUWaZ4JuV4ShLpFJ5rBlqYjySnM2MrvrjT6DZVdm9fC1elCVgt692AmmHzz6rPGRsNaOEhgaG6XmNOehfNPxj8h5tQWO4sO990GhiDmZDlm8d+FPgxq/iCa2iycSu/7fJ/Vk5UDETvFdqoW1x9iDNm6QSSbFHKfaAhCwuPF4ZjTPafYfW1mf7sK5A4SQx6dCuZuhaqC2c1je8j2vLGiu2vDEivlhyG9LULbg/Lo1/mK3ASqPdvaR1hqCR5AGq92dluSsCfJrPCYHBI1Nu8abIwp6A16L2YcFF/LRW3Bl6d3U9yxGvSoOKIDkktYFPIf9EROtEukzOgLPo/IdaV4yXNYMrOO0IbYJILvHXDXltOuj701VUB88fOShf65Q6FsxMUNuPkv4ZFgb+uaTIJHTfj1ggfj3mjOV4Fgjt7fjP//NKWOhKKWlX/XG22+Kz6K+iwXg8k1dsarncV3Pn0dVwFgTLh6O/FnWo+Q2kGS1g5zxezIzY8yyMca53Tce6xNqAciq8dXt7wwyZATRNkKw1Pmmi4qENL6h1OGwzCLwZ23cPw5mLg3sA30bZ7qxoIplaC72wqXbm3gUjqL9pD9iSHXKAyTH8zL/2n/oWoGFPG+6Op+RsVVhvK0R/77qJrmdet6f5eQckMoSlaMpFCCr6micDp6vU0hovKmcwgZknE8yYM1OIY4Y11fXkurBCwbovTaBgxN9/fyuF0o50ozOneWUQDQYiM1GAM=",
                                        "page_age": None,
                                        "title": "Bitcoin Futures,Jan-2026 (BTC=F) Stock Historical Prices & Data - Yahoo Finance",
                                        "type": "web_search_result",
                                        "url": "https://finance.yahoo.com/quote/BTC=F/history/",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "3 weeks ago",
                                        "title": "Is Bitcoin a Buy, Hold, or Sell in 2026? | The Motley Fool",
                                        "type": "web_search_result",
                                        "url": "https://www.fool.com/investing/2026/01/04/is-bitcoin-a-buy-hold-or-sell-in-2026/",
                                    },
                                    {
                                        "encrypted_content": "EtQKCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDPx63uHLEVLqY3ZRixoMEeajlrE1DNlaPy7aIjACU2K9k3tezQCVSyAep8nclSgFLCgIKz+9ws0pzZfaT2qcJaGj6oPD8PBQu031xcQq1wkiZ1M/ohzJoWyaPbJytGvBaIBSEaReZ99dWoj4K+d99uTGLRKSE5ZqgON7Lj1R1KdmLXi4X6etWFS1AX+j556mGhwRl7xHzZVRdFS6z0YMIYqKiHZ/FU63s8yx3IARiPk/xJ2VmUMCLgLv27RMhbrDCYttVgZOZVjCbh3GKUI+1zKcLoyrJs5Lyn7v4Ler7F9ivD7J6oLa+D7a8jx76jrcpZ813BG7XgW2hQozSu37dEZi9SrPeGFd8MCQ4mq78+dT7VyeICRqNMQIkqTtBTzajtEKr/LRzRbaes5ccOO63yv2M42Mdo2ZQ0OdojTng4asgnAu60shQwbE8MS6DYAmfdbaYnFZAq6bw5VuNaeDvZ9249OxEE6lNeRPsiK2yyX2jjGXImKS/YNzYDehryGRMjNnlKkMbhWptzxlS1+uUsj5a475XAJocjjAgwS6u6SWNpuQ4j5BL7PjQkrvuH0GBsdNhI/rnCDt62pvBQ7IRMBuQFIIFzib8sPS9Xa1Bin0t6qEfDwqBkKZg3q+KpLRtB41CKG8VGrg05xRzHZb4SXCFPgUE87OZC4vGjTHYCvUR05iY2f58HKZU2fGur/Tw5VMMJyusaln4FEZkkCrvv2RX/QFM+Yj+jXrXmbMBCb4jlpCe+GsvSifQ7KXl/DVsUZpBw21QV1TDZ2mGAukhNexQVYmgyFBM7hA/vV6pVntGysUw/FHeUv6MBs6orKM7Zn/EJoRfIofKCOdO9spFYkULAUp3VqIB6mEkifqiOxQHyz5F/TWC+AGunu2ikDwGCpQEU2yLz3tvFdV1DVSK3eNhZBALrKhKEKVqhys+zWTcu1DBUP8AEdTI4HYyPo/HZbWym58p9l3wcPgSNepFaHVJLfYyZb6QcpPiz/YcAi4JSj4lY5Vz+9H/2NkUqK53p013WCBYbFqhEqr54cPCmaup6ygCNiuUZvqPLfAsn9+kFoZN+FuRNUhcF6a4BdtRzU/XuaHRdJOAiCEVE3rlvtcQ3ypL+NZvehK9Kp5zQCaV7Aoh+MwWbWzDzhDJY99V30nXdE1P7E5HIOuH1S+hEplvMa5ut3Pjiy3PjcDFUjohyvgxjqyLjPj1JRpf63Otg5xGsGoxI02UmVMZzFnzHNS5qNhvDQRS8ahq8goFGgx4iiI8b3YXrkbOb5HBMW0QzbPI7AueZYAmg6EwvryQJsQGwzt64dQUllpLMJjMJYVSmSgfmNUrpSDnbKJlFDBe1kr+jrHccr8rc0bA3VLmiM8+ulQog1kHfv9tCE9xgSS2ip9oHmZ/xySKJmCrthFcxDcURLlmZOfetnj//rOtyQDFH3e9w+rhK+3YRAMHZgM/WhIK5gsr7NMjR8hPLTEtVnSjESkXqHbC9W656GKMkUsJmHpWihAEDrUaZjMYdpmO4ObpS6sVxcPfIuL7vX7yYpbg9o7+siMVg7BrA5tZJ09UjQlsAm3qOUz+RbA8+i+TzVyugQdqjuk58CBhj84ImMoNE49P0DcZRHrkHHdPHM91kLjXnoC2pvVv3nauc9dJH1ZciCEqymXeWEko/GZ8Qa8VnwTUDgY9YXCrEEUCNdceQyhc4mKdF8BOVN9WtlckNuR4Bjrsag0unYEhRx2b5mkCmd5dvRWNZICX1wHGcWK2O8Rf1cYAw==",
                                        "page_age": "1 day ago",
                                        "title": "Bitcoin Starts Week on Shaky Ground as Uncertainty Lingers - Bloomberg",
                                        "type": "web_search_result",
                                        "url": "https://www.bloomberg.com/news/articles/2026-01-26/bitcoin-starts-week-on-shaky-ground-amid-geopolitical-jitters",
                                    },
                                ],
                                "tool_use_id": "srvtoolu_01L3JVYNa5X5schrHemWyp2J",
                                "type": "web_search_tool_result",
                            },
                            {
                                "citations": None,
                                "text": "Let me search more specifically for Bitcoin's price on January 1, 2026:",
                                "type": "text",
                            },
                            {
                                "id": "srvtoolu_01PbDGQne463Rs2sWQwZtSdV",
                                "input": {
                                    "query": '"January 1 2026" bitcoin price historical data'
                                },
                                "name": "web_search",
                                "type": "server_tool_use",
                            },
                            {
                                "content": [],
                                "tool_use_id": "srvtoolu_01PbDGQne463Rs2sWQwZtSdV",
                                "type": "web_search_tool_result",
                            },
                            {
                                "citations": None,
                                "text": "Let me try another search approach:",
                                "type": "text",
                            },
                            {
                                "id": "srvtoolu_01Nxz1Z2LdV3aJko2jVBEh33",
                                "input": {
                                    "query": "bitcoin New Year 2026 price January 1"
                                },
                                "name": "web_search",
                                "type": "server_tool_use",
                            },
                            {
                                "content": [
                                    {
                                        "encrypted_content": "EqYRCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDIFlxoziXlqk03n+GBoMpE0uoppD546sstzJIjDzRXZsAIqwy28tOoKp7PlzsDJASb/l1mvqPiAGAiO4sVy049AM0JAA0fWJyYh6VyoqqRBz0nyxhLr1I1BLygmIPi8kBP3YQVu3Iu30mOYrd4x4eubeQZzikl/luEoaW3L4/GTrFBsOnOBwGjF9Q9rqYftVWu57W03RKRRu6SIlvtHF3xWJWoMBGz1eORGrxVhnA1N8N1ohEq5YzMzTgPjIlQMuQj16jCF2Odhtda+mN6SKWJZUrooNpTCmxHbLjbUdGYDF8Mh9qYl75b+uHxvfGOtfZkH2Ah/jKNlRNDoJzIALWy64w6dAWwTl1ObXBYWQO3EqgZfH/vP9Ju016cVMyvArMT/KT4bPH1mI890/dmmUgoelRAZ5Fo9+6+pEG+S+fcsTOOhISpXU5XpigHj2IFMMlmkyMqQ+BDpmicnW+t8tfRI2mcnak2dhePBS1Nm4+cPPxqpmPjXwKbtMTlrZ2tykcQVc8FPCHNDJRlFTA7g1Tbii7wbRMx2QZGLFaJkaMYsR5jQWUOE1duoquO5HeMQ4hWvS5Cu1O6eiALcTE8WgpnEsLF1YQZ+3vq5HKXkUsOd3VrpJkv2KwWEnVwN9FC4zxNRxn0ibEvTo4lGzs7IQFbX5Cif89QLqYfqTx3g8gjc0jfblFVVOhmRBC0Gi/7FdAaAsCjIN8D8aGPGR7MVl1vu4R7KeOni/jB5SGT2Ku9Gl9XhhskEvE1uMd6ev0bH3ArMmS1LTUu5Q0uzWzL6kqWPzPXrCdMbIrIzhd5lrRA2m5ulmBWDvPznRrmiUSN63IBtXLR+KQRoWJr4rvxUVs4mGlqIDwgvK2C3wBqbqR23ZHjHXDrICO5b+nhdAk64/1EIjRJakVZa/DiLoRHq+5+7MdwnCJqD6e8Kn4G+yFUNXIRdeyIHmOj7MK6q92FrsljeFoRSSBnUsK6Mm/oQr7n7zUHlwuyEAfcP7JyTk4GVMZ7Pq+F8pH2sqiC374gLgmZLEqyuG67QPgZ+jtnP+9T3NMP+pqTl4XMDPq1If9Qct3eOAPWaYAKYtZO0yF9yL5k7093be6gxUwfZTv3qm5XkX7QuiCgVcPSLASvt5n/3LUH6Wn1v6nLTYg1AktR1M0ZLIKYG8RoNp8Oov1GUd51e/vOeSzU75texLEnWvbcZ/n+ffJhzOqTO/KUkeGzmAEndo7HUOhKJ8L3KIQ1WyOynBS7zhpdVg5l7QRyHQkAfPnIdBGZaWAu4PTcHCaHj/5CrSkKsD0aqf7Qreccd0TFJmop+KvUM4PnmuNn4qQWbtW/SRCsCFeHeCkb/08UlC0xqGEdQJ/sbeTCQD9eBCu5uGfwLu4ursj3USF30FA5OaMYwYkJF1k2yU27ewc/ZUPcYP+LXg0MnM5qIiOzW0yxJ602Czh8n0QQEhnjlOUisAMWgMr36BacpSDivnaIY2PXPvcQ26hQqov/Lwu4nF1KPPlnfizge4YFGUp4xLXjfBzCc3MQfoiPgTrIS1xmp8yQGW3wjYD8I4JwJxVOZIZvggfirK32GRkJXSckcg1Sz/zb6PBSy3uMZk485c3BuvEfswT4tlkHdib8mkd7Ux7KivBJS1jl6cMU5vdrbdyivHLosugGyiDqJXtSjZc855mpMUgC6CO0L9sUlZrXRf/hlbhzAOBjfXT5TycgXUqWinYhhQw86Z4EhPaRnPnOE3DODxbzCpNE1PYrHry68XkFa7OR0h/c3O+fu9GDZvAmjXlbT8+ieqNkGljFwyThKN55p8lmoVTxcQDUAw2/DkGlp6vNh3CsnUxx8cE+b+iaexZ/dbr2R0nhqPG3BnBJIQfTGsycf09qFSABZfEnQBY0O3ZoxKNlUZLl313kpbUREuNxUMPZ9RGJ13qkZpMNdVbjUUYXqXUl5Czm8vAl6y0RfxkIU/m7AYu4PrLWySibf5WCfJm1/hVCtU6NzhiQqPlf/dwgb6f0wIScOdu9n0jrU29MAJDsjchOFdSg+FuKwyr8knuxSaYnxa8W7M4DUr0DxTD4km6rdnthnK8rNDRHNEcO0XBLxuoX+sy89JK7ywsuub1ERJjeiavQ4Cwe3bvGgwnB1TkBNQkSdDPuwzysiyAkWhQ1dzDeRohi/F28pLouRUsxTIESZriQbV3nIV9y8qaA2bv4DZ9BoOLaBLX9oUTan6squRGZREreEFETnEIRL7Ko8+i2Hzp8aIxuUFN5LSbdqV9q/CxEIAD4w77K4pnNGlEh52zEA/XVqSIzT3OtaXY/vT5/d1pIKl+7fyTdP5YQymFm/k7h01wB2SQfE2Yp1E7Pj0nF3M7WrZZ7/Tt0ZAyVuGj5r02yxbM5kZMYDiZPJ0WWIEGABWulWDjPGpZd+cNnSJqWOKHqAth4xLzj2DvzUzQ6MdLFw5gXavvgav9olAXfjnAB9/UPk2xpmQcFUjbXQzgMR8Fm6laZKy0VS3/CNrW/rwQcfyAAgjvOrAyx2k43O0nE1AEqAU1sx6swzU/WVvmiP9ANx+eGLhu7TEhXTRg9GS115JmabOdoMXfoqD1wXjEbr00bIwb+8CObshn8D/XvZTi7ETT2pvCxmgbA80Zfiggq2RfMg7azwdgb+k3bFr9Q3NWZV5j4W6t/4rJEjDlALw2WRt5ozx74AHwMeJgHjdn5CncIUqwve3xLPtj1j3B5XETuiKUwSiIBqySvDaMrw0WF9mZAXGD6oTtrpSBgcO2R5Zho6edBzR2ECloy1MYiZPURFWRKgfTtqUb+68GLkqQNX151DJ0hdFbT46RbdOgLL+90Dx4EDIvtNMHs8pek5Ia8MeNHzmz20/++hcPHge6B9l9AXiflDyjYplle3CcHTarSWKFKTvwv4w46Q3GAM=",
                                        "page_age": "1 month ago",
                                        "title": "Bitcoin (BTC) Price Analysis for January 1 - U.Today",
                                        "type": "web_search_result",
                                        "url": "https://u.today/bitcoin-btc-price-analysis-for-january-1-0",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "1 day ago",
                                        "title": "Bitcoin price news: BTC holds near year's low as precious metals continue garnering attention",
                                        "type": "web_search_result",
                                        "url": "https://www.coindesk.com/markets/2026/01/26/bitcoin-stuck-near-usd88-000-as-gold-s-and-silver-s-record-breaking-rallies-show-exhaustion-signs",
                                    },
                                    {
                                        "encrypted_content": "EqoFCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDJeaDGW/2STGPg4QARoMlulidybFnroOy7PfIjDW//MHvv+7FnApfYfMCFl8d0AN3wiVbLDHgsqsoDxsr30WZa6NJ0x62TJJLoIFkO4qrQQHpFQkheBl9qP75zU+A1T7Fwbl8Fkijo/zqzR6OZUBPOv8e24JXFzVFm6JV8l27xCFfbHtpn6pyILZSBEFN+/i49jqZCCIhW6Hah5ZadlU3ebe9ZEy38r+FpY8tpbeBNxot2irYI1wBTDe/QZGvbQVHRlNZ01B8y+8wMuoP3uCE2+b+OvO0qlcYntwg3OqbwaRWWjXf7P6nP6D6LfKtWYj19eRWE83J1ZE2tvayQ/LoGNqIoOhyd1DEeiVCW1sHrRA8sal18nEQUrh0lKLP5/XYJaCG6ExamKavtUbfuHMyNlneb/GH4H6NwXoh2fTJy+Ec7Z32HG9NjX1vj1C1pr4idjohGwaXZ9s0U7W6q3CBnhJHVupMYDwVSMFJXDe9h/chzZlClL7YxVdTtduRNF2BVLGIQZnY3zll/izByS+tQSg4bcZDcGdoWdSHV3YuMrR8Hb7f91ktfSok9KZgNMfnwbE2BItfRUrTae/Px6xGSFPK7YWbqfaJ9eGVER8yBgVcqpCzJYQf+d4wAefXmRxsvtS1TEH3jq8ypjLkvl2Tmhqgm0AMIX7SElsPAaJYwigwd3HL8l72VwOXXpGvojfKDSmYrSn3Rg5r77aO3MG98aQ9zsWMkscHgXrnJ2O9XMFBhAk6Q9fTtucCOs/84KPe0jyPgZdIfxSoBY1BtdgP64jheS3kizdvmZSQXhc/rvrUAddws5MUP7r8+sGxJpAPJSvqQbywaCB0cJxmxgD",
                                        "page_age": None,
                                        "title": "Bitcoin Futures,Jan-2026 (BTC=F) Stock Historical Prices & Data - Yahoo Finance",
                                        "type": "web_search_result",
                                        "url": "https://finance.yahoo.com/quote/BTC=F/history/",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "1 month ago",
                                        "title": "Bitcoin Price Drops 1% in New Year’s Eve: Here is a Critical Level to Watch in 2026",
                                        "type": "web_search_result",
                                        "url": "https://coinpedia.org/price-analysis/bitcoin-price-drops-1-in-new-years-eve-here-is-a-critical-level-to-watch-in-2026/amp/",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "4 weeks ago",
                                        "title": "Bitcoin price (BTC) news: Rare U.S. session gains have bitcoin trading above $90,000",
                                        "type": "web_search_result",
                                        "url": "https://www.coindesk.com/markets/2026/01/02/bitcoin-pushes-above-usd90-000-as-traders-eye-change-in-pattern",
                                    },
                                    {
                                        "encrypted_content": "Eq8CCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDKuy9ujMhxrvybVNuBoMkdDbaLVZhkXvBvIXIjBvboNfnxgJOH9eXZ4qdPqCknJ653BScVNStR0yMuleMp1HN0sbSS4Q4fmARNIMaqoqsgGNIzGzVWOI4IzwPXTnroVX2HM1PwU37g52gBDaVxaKzUm1KKdOtu/vok9agnbcwiQW903ri53pSau1gzZrZC3NfGGJvrtSXMHb08dnaMXmE2o1VWAWJYStLlORQbvuPu7F8JkCFHslpWmbSHZ7UfzDGwh1QOlm0dyvYVPompei8i4Lq1ZaVCpeQqVQtxUG5xpWwvLwIqICUneYs0ST2W9803TLT9+7iyt9nodZdBVCVsVWGAM=",
                                        "page_age": None,
                                        "title": "HISTORICAL BITCOIN PRICES ON JANUARY 1 🎉🥂 2026",
                                        "type": "web_search_result",
                                        "url": "https://www.binance.com/en/square/post/34505018894106",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "4 weeks ago",
                                        "title": "Prediction: A Single Bitcoin Will Be Worth $150,000 in 1 Year | The Motley Fool",
                                        "type": "web_search_result",
                                        "url": "https://www.fool.com/investing/2026/01/02/prediction-a-single-bitcoin-will-be-worth-150000-i/",
                                    },
                                    {
                                        "encrypted_content": "EpkDCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDCoQzTuDMp025tS8aRoMKofnRBsWHCBrX5s5IjBPZz/iGNjn5Ir9m4EkfA+pdXQroAhtcoXlTiDkhbzgP9HWZGtesREezA9oCodoRPMqnAJR5th22Iu/pqnL2P+HMfiWd5GDTxvwPFzn2PuZZbE+6Wq/Z/cTFBpRk6Z8fGZ3hRYJpT6XlkcHPgL4xqqX43KmGqVrSfSwo/bXEfVwYqBIbKgpOkCFzMv8xq1a3ehTrh6ZFqaV3ZHrinuaUOY97+ssVTABp4dAsKcJC+oQzs/XZkfGK9iFdoLQxRueBaQHt0gb1/YenCySQQ6KawflTMBrzwnCVJvSL5Lim+wMcW0+5ux0GE6UkE2S+csZJM0OpQY2S0Z7zMVDQUNKYZ5M+mevl0TutQZU/74ywgHLjTNyu7hbeQx2iZ2AAvPDP4j5oA8pX4/MjePL46EllQdNq3ltoqxoTBRNwaOBCnx3OKvQQ5v28wgqUCjqxDVzqRgD",
                                        "page_age": None,
                                        "title": "Bitcoin price on Jan 1, 2026 at 8pm EST Prediction Market",
                                        "type": "web_search_result",
                                        "url": "https://robinhood.com/us/en/prediction-markets/crypto/events/bitcoin-price-on-jan-1-2026-at-8pm-est-dec-31-2025/",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "3 weeks ago",
                                        "title": "Bitcoin Price Jumps 8% Into New Year As Bullish Momentum Builds",
                                        "type": "web_search_result",
                                        "url": "https://bitcoinmagazine.com/markets/bitcoin-price-jumps-8-into-new-year",
                                    },
                                    {
                                        "encrypted_content": "EpkDCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDEnl1Va8C6YYIF17cBoMgR7HQldf9g4tZ3TCIjAhXXRBZz/+KTfDk+2goWGp4M6HOYYPsiOnltUbOLz2D0Sxy//mA6JAeabHO5e3VTEqnAJIBSsnNs3tATPrkskFBJT2sEgj8lQPtYkTgzk5aQ+ciUvHqCc1LJ4/SLL4WBOagIiJQy7G/nAYVGuVsDfy/VEo13eLnmM9Ig3GKb+ENe3RiZ6ph6BCDqqpQ7MsnPcGMqpvDC7arXTCh11ZbBzzVZIQ/iTuWI2d8U6AOQMKr8cDx/MKhS1ZT8aGj0jbCkdRL56J5m9HauSmY4gIbVeurIDGp9QnQlYfKnb/AIPybjge0dJsdgCoI+mtgzpWaN2S+Qzs1jTcsloDAJPMkE7miEk20OyaUyucusZgxf8Y1NhncKYZz8oyRH5PA77A5PYpddRCP3/3KFgp1dKe+UV5KyB9Rhe2KHVRDN9CEtmfq+RhqnBTuXHcya/aqRq4SBgD",
                                        "page_age": None,
                                        "title": "Bitcoin price on Jan 1, 2026 at 12am EST Prediction Market",
                                        "type": "web_search_result",
                                        "url": "https://robinhood.com/us/en/prediction-markets/crypto/events/bitcoin-price-on-jan-1-2026-at-12am-est-dec-30-2025/",
                                    },
                                ],
                                "tool_use_id": "srvtoolu_01Nxz1Z2LdV3aJko2jVBEh33",
                                "type": "web_search_tool_result",
                            },
                            {
                                "citations": None,
                                "text": """\
Based on the search results, I can provide you with information about Bitcoin's price on January 1, 2026:

""",
                                "type": "text",
                            },
                            {
                                "citations": [
                                    {
                                        "cited_text": "The price briefly touched an intraday high of $94,352 after opening the year near $87,400 on Jan. 1, per Bitcoin Magazine Pro data. ",
                                        "encrypted_index": "EpABCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDPaPmfT227nJ/QfsHRoMedNmd8hMVSmkT416IjA68HvrIuw9tbcID7jSkKef1N8zVrL7PIu/9JDzAjyu3TXP0Xc439Y84P0FJETScLUqFAqQJ7+sHOsIA7U7Xxfsq14Z2BgGGAQ=",
                                        "title": "Bitcoin Price Jumps 8% Into New Year As Bullish Momentum Builds",
                                        "type": "web_search_result_location",
                                        "url": "https://bitcoinmagazine.com/markets/bitcoin-price-jumps-8-into-new-year",
                                    }
                                ],
                                "text": "The price briefly touched an intraday high of $94,352 after opening the year near $87,400 on Jan. 1",
                                "type": "text",
                            },
                            {
                                "citations": None,
                                "text": """\
, according to Bitcoin Magazine Pro data. This indicates that Bitcoin opened the year 2026 at approximately $87,400.

Additional context from the search results shows that \
""",
                                "type": "text",
                            },
                            {
                                "citations": [
                                    {
                                        "cited_text": "The flagship coin dropped over 1% in the past 24 hours to trade at about $87,255 at press time. ",
                                        "encrypted_index": "EpABCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDARcVQlOsltRxNu6TBoMkRq4a0pRHYVe3QcmIjC6uNvLp/mqL9elbC+SVjtuwL3ulmI9jZV+djubuiJGAXYfqQGNUvGZJE4w/f6n0CIqFAvVvBFQ+OkBC3GblLSp7LYL0yTIGAQ=",
                                        "title": "Bitcoin Price Drops 1% in New Year’s Eve: Here is a Critical Level to Watch in 2026",
                                        "type": "web_search_result_location",
                                        "url": "https://coinpedia.org/price-analysis/bitcoin-price-drops-1-in-new-years-eve-here-is-a-critical-level-to-watch-in-2026/amp/",
                                    }
                                ],
                                "text": "The flagship coin dropped over 1% in the past 24 hours to trade at about $87,255 at press time",
                                "type": "text",
                            },
                            {
                                "citations": None,
                                "text": " around New Year's Eve, and ",
                                "type": "text",
                            },
                            {
                                "citations": [
                                    {
                                        "cited_text": "The price of Bitcoin (BTC) has declined by 0.41% over the last 24 hours. ",
                                        "encrypted_index": "EpABCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDDhx3C8SR/wLHy5RTBoMQZYHz/F7P4tesbvJIjBrDhh/ohKSrFciCmdpsgneKISDtZgWoqk/POSK3LwMakQSDcP5Jqqiu/GkU2crSa4qFL2DGYLUM6LB1R0DWrj+sUkFYT5aGAQ=",
                                        "title": "Bitcoin (BTC) Price Analysis for January 1 - U.Today",
                                        "type": "web_search_result_location",
                                        "url": "https://u.today/bitcoin-btc-price-analysis-for-january-1-0",
                                    }
                                ],
                                "text": "The price of Bitcoin (BTC) has declined by 0.41% over the last 24 hours",
                                "type": "text",
                            },
                            {
                                "citations": None,
                                "text": """\
 on January 1, 2026.

The search results also indicate that \
""",
                                "type": "text",
                            },
                            {
                                "citations": [
                                    {
                                        "cited_text": "Bitcoin (BTC) price has closed 2025 trading below crucial support levels around $100k and 90k. ",
                                        "encrypted_index": "EpABCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDBORcoPuyotoFM2JLRoM5X/wF/Akt1Baw7gfIjDVDOPfL+1KexWUuBX6aUoJ4Di4JJcNtWyRCq7hlu3Myj1IdpHeOXHEvt7C5cQp/rsqFKFK8EQqdbL0V5mfNuuH3+9YTF6zGAQ=",
                                        "title": "Bitcoin Price Drops 1% in New Year’s Eve: Here is a Critical Level to Watch in 2026",
                                        "type": "web_search_result_location",
                                        "url": "https://coinpedia.org/price-analysis/bitcoin-price-drops-1-in-new-years-eve-here-is-a-critical-level-to-watch-in-2026/amp/",
                                    },
                                    {
                                        "cited_text": "After closing 2025 in a choppy consolidation, Bitcoin will begin 2026 on a high bullish note.",
                                        "encrypted_index": "EpABCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDNT8cv0GoKrlHcIdahoMQZ0A3/9cQoFe7NYJIjAgs71z5krW8FSJZ1l7PacchU4uIRaz+b9nhmW/rFVxovu/e6UfW63jprzHA+iKnCgqFHYbnyrsHEBIzfoCzrgIqxOUbHc+GAQ=",
                                        "title": "Bitcoin Price Drops 1% in New Year’s Eve: Here is a Critical Level to Watch in 2026",
                                        "type": "web_search_result_location",
                                        "url": "https://coinpedia.org/price-analysis/bitcoin-price-drops-1-in-new-years-eve-here-is-a-critical-level-to-watch-in-2026/amp/",
                                    },
                                ],
                                "text": "Bitcoin (BTC) price has closed 2025 trading below crucial support levels around $100k and 90k",
                                "type": "text",
                            },
                            {"citations": None, "text": " and that ", "type": "text"},
                            {
                                "citations": [
                                    {
                                        "cited_text": "After closing 2025 in a choppy consolidation, Bitcoin will begin 2026 on a high bullish note.",
                                        "encrypted_index": "EpABCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDFehQlv7nyt8ovIb5xoMTAjEWJtDunxSXpg/IjA0o0NvBGLYqXTZNpXfmwWMbc/Pji4+i3BHfVN+66atr1w0iLb2sz3rNPZ8oHjDopkqFDFy7A8IoaFDmmiMLFKtyLDKfU+1GAQ=",
                                        "title": "Bitcoin Price Drops 1% in New Year’s Eve: Here is a Critical Level to Watch in 2026",
                                        "type": "web_search_result_location",
                                        "url": "https://coinpedia.org/price-analysis/bitcoin-price-drops-1-in-new-years-eve-here-is-a-critical-level-to-watch-in-2026/amp/",
                                    }
                                ],
                                "text": "After closing 2025 in a choppy consolidation, Bitcoin will begin 2026 on a high bullish note",
                                "type": "text",
                            },
                            {
                                "citations": None,
                                "text": """\
.

So to summarize: **Bitcoin's price on January 1, 2026 opened near $87,400 and reached an intraday high of $94,352**.\
""",
                                "type": "text",
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
                            text="Let me search for more specific information about Ethereum's price on January 1, 2026:"
                        ),
                        Text(
                            text="""\
Based on the search results, I can provide information about Ethereum's price around January 1, 2026, though the specific opening price isn't as clearly documented as Bitcoin's.

From the AI predictions and market analysis sources, \
"""
                        ),
                        Text(
                            text="ChatGPT's central forecast places Ethereum at approximately $3,200 on January 1, 2026, with a tolerance band of about $500 on either side"
                        ),
                        Text(
                            text="""\
.

Additionally, \
"""
                        ),
                        Text(
                            text="According to the model, the most probable outcome is a base-case scenario in which Ethereum trades between $3,000 and $3,300 on January 1, 2026. This outlook assumes range-bound trading into late December 2025, continued volatility without a systemic breakdown, and steady demand emerging near key support levels. Under these conditions, the market is expected to transition into a mild early-2026 uptrend"
                        ),
                        Text(
                            text="""\
.

Another analysis suggests that \
"""
                        ),
                        Text(
                            text="In January 2026, Ethereum is projected to reach a minimum price of $2,890.90, an average price of $3,161.92, and a maximum of $3,252.26"
                        ),
                        Text(
                            text="""\
.

Current market data shows \
"""
                        ),
                        Text(
                            text="As Ethereum (ETH) trades just below the $3,000 level... as of press time, ETH was trading at $2,957, having plunged more than 3% over the past 24 hours"
                        ),
                        Text(
                            text="""\
 leading up to the new year.

**Summary**: While I couldn't find the exact opening price like I did for Bitcoin, the available analysis and predictions suggest that **Ethereum's price on January 1, 2026 was likely in the range of $3,000-$3,200**, with most forecasts centering around **$3,200** for that date.\
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
                                "id": "srvtoolu_01SWkmhU6sdk9cspeNEWzSPq",
                                "input": {"query": "Ethereum ETH price January 1 2026"},
                                "name": "web_search",
                                "type": "server_tool_use",
                            },
                            {
                                "content": [
                                    {
                                        "encrypted_content": "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",
                                        "page_age": None,
                                        "title": "Ethereum Price: ETH Live Price Chart, Market Cap & News Today | CoinGecko",
                                        "type": "web_search_result",
                                        "url": "https://www.coingecko.com/en/coins/ethereum",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "1 week ago",
                                        "title": "Ethereum (ETH) Price Prediction 2025 2026 2027 - 2030",
                                        "type": "web_search_result",
                                        "url": "https://changelly.com/blog/ethereum-eth-price-predictions/",
                                    },
                                    {
                                        "encrypted_content": "ErEJCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDCkcBzpfAp8aGBNeKBoMTwmv2PE+EDNnBr+bIjBE2Yc/pWsvLeLJbP/pmhBG5sZX7IWBqBGvtPgGaZmLO/seYSq+wGek7dqROUO0IwwqtAjJh2yVzM6ln3j/3kErGillIfjUQB2MgakpwxSEO/zSz5uhG4uXLcOpwcStuGYUpHJwTGSevi3CqajxL89Dj7HrIpFPNWNm/CACopX1JA5GTijNPGLapNCXWqYkexgdiOLCVWRf+njpYlbAAnkPK368eYoH++4KWhpcd/UD6OOh0I4yRu2/q0fwHryvZt9Iy25VPxDwcfHr739Y6EeZbMAcRtgzkC7fucPB0hRgVf8fenOHuPbtRu1c0I/jOdCRE5xVFAwhyjqdodptY9sOHfgN8EN7/G1EL5nB7obb6T6Vmcy3kzknFuGGd/8KXXLetCW4K2KeNuMWtJjdh6Fr0rlPkZHdfiOnyZ+YL/nUDp1UKRs0T11FPbBEuT+0E3GBU6U79UU8dYvaIs3lU6H5ZT2HXUHg+32XDg4KdYLuhPmE6l/JTE8+VplvJ7d9oR3iEir+tWmmNti5g54ibe/kk0Bnf3m9E14qB/yiQdErshStlsQ09wJFgn5tJeZT/rH5TuGXBwTWi29U1539HsEIi1HImbs52f3rKq4RgrsDND8irFlZYuB3NyFFlt1Qr9lvSIHe791vhNeYL6v6Q6Wpiq89Ui0A5cDyafpqzRCkgkwgWZh7ttpgy9QtPoMNrrKbHrf+/NP9npwwRT6fBz9cd3OxKpMXOtUkufq/glj37AnhV5gJ0Db3yLEKgVydAdfwk17IEayMCSSemq5+Aew3BUUJ78wIM9pu1aAtl7rRJrAxoMQ+2BoDDetS6bBFOdi3IxfJedUgu9IWm1obAlFvvHSqEp5VNFH+3D/CwOeQQTWlG+/qAiCPhcJtzEEeLBhPRmElTFg8EPA/zMhiO4eSCfocnrcMBQCciv0XxvF1cOwuJClZb9PfD2aZ9/ADJoxxN+9eGR57tZXE0FWAnQzMDAGFfxjPtLazsrg8LDcCHPPm/fO5Q4nePzqJJPRSFP3j6d+kztK8WdAVshWqZ5gUN19uSHhO1ea7/Ri7mz4oGq8jchU4Egr6FbF11Nc6BS4o8JsZJxvP08Vlo4LsvoKRPkzAZ3PoKzLyNvlHhExSPFq5LvchkTD+uGrQKt4P/gNeFtwDMshp8zELxUgApBInihBGXUVZBCgQwclA18jErGkM7W5kToWn2BlxN+GvqD/aYZnrZ1TyisVuWH1gD80aUtCSGtYeCe8Wg/RrrEtuQREa3fbdKAK53Ff1iQLKcWMLxPv05jWwQu0fhVP9w1nCB9tqVtyXnUU/msuuZqspPoIWpniRC5Gk6cfXKNpfMzyK7s6yj0xKrXebSZtq3ge2ix0nWbfN/FdC0fN1c6qB8SYEpLZDit9+1uOjgenhGtxBRJIH3xO0jdT3lR/545o8W24JEn4FMPkMCZwX7ImGg0ldEfE/my739jZ140dI+bYLAb0OQ4B8yw3Ztz9IPEljL6NMrbBi6hgD",
                                        "page_age": None,
                                        "title": "Ethereum USD (ETH-USD) Price History & Historical Data - Yahoo Finance",
                                        "type": "web_search_result",
                                        "url": "https://finance.yahoo.com/quote/ETH-USD/history/",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": None,
                                        "title": "Ethereum price today, ETH to USD live price, marketcap and chart | CoinMarketCap",
                                        "type": "web_search_result",
                                        "url": "https://coinmarketcap.com/currencies/ethereum/",
                                    },
                                    {
                                        "encrypted_content": "EpACCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDN8T3xFZXyVfboqdcxoM9Vc7/LSW+4Lj0SrpIjBPL9BUCl2qWZb10W/LximlxqRVDxEnH8/Hgcs/98z14Nkms+ENaP+J5x2g7rlLpQUqkwGoorEbjpEu/4J8r0FREehmcGrFPIDDG5biHF/vy5f5y5t+rsUzHNh/j5ONwnP0Gu9ChfGYL/AIc5mpAtzPHsrodRablqMSglMkGHwwX0bzGy83q8zGNhgkVlGFkISw6wLbNtbHXC7zf4grrQO9ZjH67iuKFsAFIkr2elnw234IBLj+jvQ93zDWQs0C3UXa9kys00kYAw==",
                                        "page_age": None,
                                        "title": "BTC, ETH price news: Breakout liquidate nearly $700 million crypto shorts",
                                        "type": "web_search_result",
                                        "url": "https://www.coindesk.com/markets/2026/01/14/bitcoin-and-ether-s-sharp-mechanical-breakouts-liquidate-nearly-usd700-million-short-positions",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": None,
                                        "title": "AI predicts Ethereum price for January 1, 2026 | MEXC News",
                                        "type": "web_search_result",
                                        "url": "https://www.mexc.com/news/331946",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "2 weeks ago",
                                        "title": "Ethereum price prediction 2026, 2027, 2028-2032",
                                        "type": "web_search_result",
                                        "url": "https://www.cryptopolitan.com/ethereum-price-prediction/",
                                    },
                                    {
                                        "encrypted_content": "EuoICioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDGoSBFhgHVSa1/n5khoMtegwAxJ9tEVcD1T8IjDhaYSsZeqZVc9bECC3cIKiq11E9S5LJ51LCZjSZjm9jI6c1143nPdQG5fYVlnfqacq7QdEEqafoYzDB4+8U+6Z+CTpBBDsxT4FGwDF32j9zAEzA7oo3GgD15o967fk2lYW9275rayQCR+kckXAk3OuGLewra/qL9bvaltxhC6V7SnLfh06khUPHfTZ4Uu7GpZbvv3dY1lY/L8wFDo7Ord3iRSW2F9oANC6JkPxEHXoLizoTVGISTDF/TlCMgXvLxqGJi2/H8PsGeUR/5+scRgXs+t9kTMH9K8q2oJ8UW8LiOT1Iza0N1bpy6cyugR2EcenJgIGnyvVRXLyIsY6wPQZB9nupsiBOyehZR/AKQ1qYyi5F/4Z1ejc5r8pHWAUyQaR+KgRh4GZtozyVFcS8ew0aEhYB7eTY4D8IiTCzqwIraCv554gdnsxSPiOsPHpEsPic3XxiR0u9aCBJtP2SBTQejtfKIZofvfVfVR8wEGKNnfxnptD5x2TEDUCLPkMbBbQB7K3Z4xWbVGzoaeSwtnholdjUguns4Df5cTCQDVASRVeM2xlGL0iyplGrL7+IvJDewbKK7YSA9RumOL52d6FAWpy8w5JKBywH51a5p2xjmwME4v5w76vWGthGEBVFWfbW5RgXa/yCTmaDvI0hg4gOi3pEzuRo6WZ2RG125NtHpJaadqGDpo3gDNPxaqJEPSND9Z7wR7irsc8yqRXhnu/GO9DbZXzdiHfyY5RNsWdMQKwxtWP/pHAlbBeeiiU3V4u5fPm5mz+iPARIp4FGo9HcJP9V7cTLvAnu9zNUXDO/OLmqgJZ1yLu0o4GZCXOp6K37hN5F89IlB5RLB/Fx6HpIbriMWSeCSPkk7BCugN64cExhI9Yrgiua7i3O2NUM/1EzGaBAPLbzMlYwsLOmwkBaOaI9HLSTr2kg2m6vJ+BGy0i2krEbn6XF1YQoqFEGkqIWttXQCWC6KU1zSNpvoCDc3mlnaH/Spw2t1YutuyMzThmGQtUi9H1Vpw1H1HXDI2WT7kSpLtMMgW3Qt3XXUwIepLHjv+ar5yY818gkKp2KmqQ0xmt7qljZUeApXtOQRbl2rB0/vYDXCyASxPvoezNuejbHZ8CmUqrXoW1a+VL66lrWjkOE9Sn2JUK3Bak52wzckFSOVQA54dhnXexA9AhaI+RIjyub+a10Dlrp/PlW0L3CMxbYsI2MAYYG9e6XqU/vqKOrZFR61Zz/JgrBRs4edr18zmLH6oeD5ljeE4+e7ALWaGkDbhu66cXTsEpwlnMrU2wYUiRG6oNJmwT8ltTE0mX9JVWax0cQNU3XuJUSA4daYc56KZXkG8btS1mj+MCLMZkHch6+GNYB3HuJNj0btru5SL+q2CU6ku4+lQH22YrQI0JsbBoGjkKzbUcDNYYAw==",
                                        "page_age": None,
                                        "title": "Ethereum price today, ETH to USD live price, marketcap and chart | CoinDesk",
                                        "type": "web_search_result",
                                        "url": "https://www.coindesk.com/price/ethereum",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": "4 weeks ago",
                                        "title": "Ethereum (ETH) Price Prediction January 2026, 2030, 2040 - 2050",
                                        "type": "web_search_result",
                                        "url": "https://coingape.com/price-predictions/ethereum-eth-price-prediction/",
                                    },
                                    {
                                        "encrypted_content": "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",
                                        "page_age": None,
                                        "title": "Ethereum Price History and Historical Data | CoinMarketCap",
                                        "type": "web_search_result",
                                        "url": "https://coinmarketcap.com/currencies/ethereum/historical-data/",
                                    },
                                ],
                                "tool_use_id": "srvtoolu_01SWkmhU6sdk9cspeNEWzSPq",
                                "type": "web_search_tool_result",
                            },
                            {
                                "citations": None,
                                "text": "Let me search for more specific information about Ethereum's price on January 1, 2026:",
                                "type": "text",
                            },
                            {
                                "id": "srvtoolu_01K8Chw3JSh4cDj81iFzAEQj",
                                "input": {
                                    "query": '"January 1 2026" Ethereum ETH price opening new year'
                                },
                                "name": "web_search",
                                "type": "server_tool_use",
                            },
                            {
                                "content": [],
                                "tool_use_id": "srvtoolu_01K8Chw3JSh4cDj81iFzAEQj",
                                "type": "web_search_tool_result",
                            },
                            {
                                "citations": None,
                                "text": """\
Based on the search results, I can provide information about Ethereum's price around January 1, 2026, though the specific opening price isn't as clearly documented as Bitcoin's.

From the AI predictions and market analysis sources, \
""",
                                "type": "text",
                            },
                            {
                                "citations": [
                                    {
                                        "cited_text": "Source: ChatGPT · Balancing these outcomes, ChatGPT’s central forecast places Ethereum at approximately $3,200 on January 1, 2026, with a tolerance ba...",
                                        "encrypted_index": "EpABCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDH1uUh9svN/bO8DCNhoM2nK5iroBW09VIiB6IjC+OIiNAtlaiRAT/0hu9fdvLBxypr2vNXb+w4aSbCAvdQ+iX7ce5NTgim2j4P7PvaEqFGoeehoZWW7q0xoqfeRGwkk3TWbIGAQ=",
                                        "title": "AI predicts Ethereum price for January 1, 2026 | MEXC News",
                                        "type": "web_search_result_location",
                                        "url": "https://www.mexc.com/news/331946",
                                    },
                                    {
                                        "cited_text": "Source: ChatGPT · Balancing these outcomes, ChatGPT’s central forecast places Ethereum at approximately $3,200 on January 1, 2026, with a tolerance ba...",
                                        "encrypted_index": "EpEBCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDM+WjY2ZwAdj3QsfFRoMeZeR6CBiLSLxuPo2IjCnIwHMAfwIRrBrs8yKVOuQM/312PVX2ZFQDBKFERcMz1/ZoPQACef3XYuTGl6oEd4qFctzLNwTY820FRpEmbLwNZOF5XLJlRgE",
                                        "title": "AI predicts Ethereum price for January 1, 2026 | MEXC News",
                                        "type": "web_search_result_location",
                                        "url": "https://www.mexc.com/news/331946",
                                    },
                                ],
                                "text": "ChatGPT's central forecast places Ethereum at approximately $3,200 on January 1, 2026, with a tolerance band of about $500 on either side",
                                "type": "text",
                            },
                            {
                                "citations": None,
                                "text": """\
.

Additionally, \
""",
                                "type": "text",
                            },
                            {
                                "citations": [
                                    {
                                        "cited_text": "According to the model, the most probable outcome is a base-case scenario in which Ethereum trades between $3,000 and $3,300 on January 1, 2026. This ...",
                                        "encrypted_index": "EpQBCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDBmtxgaZN7LpueLxQBoMjZpA1rgWYXB+wPK8IjDshZ6xxNteTvSbiCfPF6YUCYqHxCJAPkVcuTXHvC7kajhr03xJqr++iObiaxznH7oqGL18yhDOQgaz2XpplVj9rUo4+8akQlBWKRgE",
                                        "title": "AI predicts Ethereum price for January 1, 2026 | MEXC News",
                                        "type": "web_search_result_location",
                                        "url": "https://www.mexc.com/news/331946",
                                    }
                                ],
                                "text": "According to the model, the most probable outcome is a base-case scenario in which Ethereum trades between $3,000 and $3,300 on January 1, 2026. This outlook assumes range-bound trading into late December 2025, continued volatility without a systemic breakdown, and steady demand emerging near key support levels. Under these conditions, the market is expected to transition into a mild early-2026 uptrend",
                                "type": "text",
                            },
                            {
                                "citations": None,
                                "text": """\
.

Another analysis suggests that \
""",
                                "type": "text",
                            },
                            {
                                "citations": [
                                    {
                                        "cited_text": "In January 2026, Ethereum is projected to reach a minimum price of $2,890.90, an average price of $3,161.92, and a maximum of $3,252.26 ·",
                                        "encrypted_index": "EpEBCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDGWCtxOodU1lMiDZGxoMn/m7jswewmswVVXWIjBmGb+cBx3ytSrb1tGiTtzW+XBOzp2xdEk9Gki3FZ9mIs6am8t8jU3gGZQGYAjLXusqFfZRJ3WED6m5H0iqcuP0Sg+u1wjS4RgE",
                                        "title": "Ethereum price prediction 2026, 2027, 2028-2032",
                                        "type": "web_search_result_location",
                                        "url": "https://www.cryptopolitan.com/ethereum-price-prediction/",
                                    }
                                ],
                                "text": "In January 2026, Ethereum is projected to reach a minimum price of $2,890.90, an average price of $3,161.92, and a maximum of $3,252.26",
                                "type": "text",
                            },
                            {
                                "citations": None,
                                "text": """\
.

Current market data shows \
""",
                                "type": "text",
                            },
                            {
                                "citations": [
                                    {
                                        "cited_text": "As Ethereum (ETH) trades just below the $3,000 level, an artificial ... As Ethereum (ETH) trades just below the $3,000 level, an artificial intelligen...",
                                        "encrypted_index": "EpIBCioIDBgCIiQyMTdhNjA3Zi1lZDVlLTQwYWYtOGE3ZC1mODNlZDUyZDU5ZDYSDH9aA8O5EGwWox5bpRoMO5v3+TILwNvwqM6yIjAjtWNBH4mYotCcRb98sB1TCo21EwXLHDBDvuF18G0T61S9+TOpdwJ7Yh9eS0UXxOQqFuy1WdZ5iWLH0jnJEH+gEZ/SKgK5DIIYBA==",
                                        "title": "AI predicts Ethereum price for January 1, 2026 | MEXC News",
                                        "type": "web_search_result_location",
                                        "url": "https://www.mexc.com/news/331946",
                                    }
                                ],
                                "text": "As Ethereum (ETH) trades just below the $3,000 level... as of press time, ETH was trading at $2,957, having plunged more than 3% over the past 24 hours",
                                "type": "text",
                            },
                            {
                                "citations": None,
                                "text": """\
 leading up to the new year.

**Summary**: While I couldn't find the exact opening price like I did for Bitcoin, the available analysis and predictions suggest that **Ethereum's price on January 1, 2026 was likely in the range of $3,000-$3,200**, with most forecasts centering around **$3,200** for that date.\
""",
                                "type": "text",
                            },
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [{"name": "web_search"}],
        }
    }
)
