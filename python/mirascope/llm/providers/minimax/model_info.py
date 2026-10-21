"""MiniMax model information.

Maintained manually based on https://platform.minimax.io/docs/guides/models-intro .
Keep this list in sync with the strings users are expected to pass to
`@llm.call("minimax/<model>")`.
"""

from typing import Literal

MiniMaxKnownModels = Literal[
    "minimax/MiniMax-M3.1-Flash",
    "minimax/MiniMax-M3",
]
"""Current MiniMax model suggestions; explicit legacy and custom IDs remain valid."""
