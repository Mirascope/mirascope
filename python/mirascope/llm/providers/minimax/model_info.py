"""MiniMax model information.

Maintained manually based on https://platform.minimaxi.com/document/Models .
Keep this list in sync with the strings users are expected to pass to
`@llm.call("minimax/<model>")`.
"""

from typing import Literal

MiniMaxKnownModels = Literal[
    "minimax/MiniMax-M3",
    "minimax/MiniMax-M2.7",
    "minimax/MiniMax-M2.7-highspeed",
]
"""Valid MiniMax model IDs (chat / LLM)."""
