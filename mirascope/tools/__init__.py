from contextlib import suppress

from .system._file_system import FileSystemToolKit, FileSystemToolKitConfig

with suppress(ImportError):
    from .system._docker_operation import (
        DockerOperationToolKit,
        DockerOperationToolKitConfig,
    )

with suppress(ImportError):
    from .web._duckduckgo import DuckDuckGoSearch, DuckDuckGoSearchConfig

with suppress(ImportError):
    from .web._httpx import HTTPX, AsyncHTTPX, HTTPXConfig

with suppress(ImportError):
    from .web._parse_url_content import ParseURLConfig, ParseURLContent

with suppress(ImportError):
    from .web._requests import Requests, RequestsConfig

__all__ = [
    "HTTPX",
    "AsyncHTTPX",
    "DockerOperationToolKit",
    "DockerOperationToolKitConfig",
    "DuckDuckGoSearch",
    "DuckDuckGoSearchConfig",
    "FileSystemToolKit",
    "FileSystemToolKitConfig",
    "HTTPXConfig",
    "ParseURLConfig",
    "ParseURLContent",
    "Requests",
    "RequestsConfig",
]
