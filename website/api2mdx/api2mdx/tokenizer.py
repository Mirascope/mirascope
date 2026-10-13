"""Tokenizer for Python type expressions.

This module provides functionality to convert type expression strings
into a sequence of tokens for further parsing.
"""

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Types of tokens in a type expression."""

    IDENTIFIER = "IDENTIFIER"  # Simple type names like "str", "List", etc.
    OPEN_BRACKET = "OPEN_BRACKET"  # [
    CLOSE_BRACKET = "CLOSE_BRACKET"  # ]
    COMMA = "COMMA"  # ,
    PIPE = "PIPE"  # |


@dataclass
class Token:
    """Represents a token in a type expression."""

    type: TokenType
    value: str

    def __repr__(self) -> str:
        """Return a string representation of the token.

        Returns:
            A string in the format Token(TYPE, 'value')

        """
        return f"Token({self.type.name}, '{self.value}')"


def tokenize(type_str: str) -> list[Token]:
    """Convert a type string into a list of tokens.

    Args:
        type_str: The type expression string to tokenize

    Returns:
        A list of Token objects representing the lexical elements of the type expression

    Examples:
        >>> tokenize("str")
        [Token(IDENTIFIER, 'str')]

        >>> tokenize("List[str]")
        [Token(IDENTIFIER, 'List'), Token(OPEN_BRACKET, '['), Token(IDENTIFIER, 'str'), Token(CLOSE_BRACKET, ']')]

        >>> tokenize("Dict[str, int]")
        [Token(IDENTIFIER, 'Dict'), Token(OPEN_BRACKET, '['), Token(IDENTIFIER, 'str'), Token(COMMA, ','), Token(IDENTIFIER, 'int'), Token(CLOSE_BRACKET, ']')]

        >>> tokenize("str | int")
        [Token(IDENTIFIER, 'str'), Token(PIPE, '|'), Token(IDENTIFIER, 'int')]

    """
    tokens = []
    i = 0

    while i < len(type_str):
        char = type_str[i]

        # Skip whitespace
        if char.isspace():
            i += 1
            continue

        # Handle special characters
        if char == "[":
            tokens.append(Token(TokenType.OPEN_BRACKET, "["))
            i += 1
        elif char == "]":
            tokens.append(Token(TokenType.CLOSE_BRACKET, "]"))
            i += 1
        elif char == ",":
            tokens.append(Token(TokenType.COMMA, ","))
            i += 1
        elif char == "|":
            tokens.append(Token(TokenType.PIPE, "|"))
            i += 1
        else:
            # Handle identifiers (type names)
            start = i
            while i < len(type_str) and type_str[i] not in "[]|, \t\n":
                i += 1
            if i > start:
                identifier = type_str[start:i].strip()
                tokens.append(Token(TokenType.IDENTIFIER, identifier))

    return tokens
