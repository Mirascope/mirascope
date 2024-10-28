from .requests import Requests, RequestsConfig
from .search.duckduckgo import DuckDuckGoSearch, DuckDuckGoSearchConfig
from .web.parse_url_content import ParseURLConfig, ParseURLContent

__all__ = [
    "DuckDuckGoSearch",
    "DuckDuckGoSearchConfig",
    "ParseURLContent",
    "ParseURLConfig",
    "Requests",
    "RequestsConfig",
]
