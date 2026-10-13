"""Parser for Python type expressions.

This module converts tokens from the tokenizer into structured type model objects.
It implements a recursive descent parser for various Python type forms.
"""

from dataclasses import dataclass

from .tokenizer import Token, TokenType, tokenize
from .type_model import GenericType, SimpleType, TypeInfo, TypeKind

CALLABLE_PARAMETER_LENGTH = 2


class ParseError(Exception):
    """Error raised during parsing."""

    pass


@dataclass
class Parser:
    """Parser for type expressions.

    Uses the tokens produced by the tokenizer to build a type model.
    """

    tokens: list[Token]
    position: int = 0

    @property
    def current_token(self) -> Token | None:
        """Get the current token or None if at the end."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def next_token(self) -> Token | None:
        """Advance to the next token and return it."""
        self.position += 1
        return self.current_token

    def peek_token(self) -> Token | None:
        """Peek at the next token without advancing."""
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return None

    def expect_token_type(self, token_type: TokenType) -> Token:
        """Expect the current token to be of a specific type.

        Args:
            token_type: The expected token type

        Returns:
            The token if it matches the expected type

        Raises:
            ParseError: If the current token doesn't match the expected type

        """
        token = self.current_token
        if token is None or token.type != token_type:
            expected = token_type.name
            actual = "EOF" if token is None else token.type.name
            raise ParseError(f"Expected {expected}, got {actual}")
        self.next_token()
        return token

    def parse(self) -> TypeInfo:
        """Parse the tokens into a TypeInfo object.

        Returns:
            A TypeInfo object representing the parsed type

        Raises:
            ParseError: If the tokens cannot be parsed into a valid type

        """
        # Start parsing
        result = self.parse_type()

        # Check if we've consumed all tokens
        if self.current_token is not None:
            raise ParseError(
                f"Unexpected token: {self.current_token.type.name} '{self.current_token.value}'"
            )

        return result

    def parse_type(self) -> TypeInfo:
        """Parse any type expression.

        This is the main entry point for parsing a type expression at any level.

        Returns:
            A TypeInfo object representing the parsed type

        """
        return self.parse_union_type()

    def parse_union_type(self) -> TypeInfo:
        """Parse a union type (X | Y | Z).

        Returns:
            A TypeInfo object representing the parsed union type or a non-union type

        """
        # Parse the first type
        left = self.parse_primary_type()

        # Check if there are union operators (|)
        if self.current_token is not None and self.current_token.type == TokenType.PIPE:
            # Collect all types in the union
            union_types = [left]

            # Process all parts of the union
            while (
                self.current_token is not None
                and self.current_token.type == TokenType.PIPE
            ):
                self.next_token()  # Consume the | token
                union_types.append(self.parse_primary_type())

            # Reconstruct the original type string
            type_str = " | ".join(t.type_str for t in union_types)

            # Create a UnionType (represented as a GenericType with "Union" base type)
            base_type = SimpleType(type_str="Union", symbol_name="Union")
            return GenericType(
                type_str=type_str,
                base_type=base_type,
                parameters=union_types,
                kind=TypeKind.UNION,
            )

        return left

    def parse_primary_type(self) -> TypeInfo:
        """Parse a primary type (simple, generic, or tuple).

        Returns:
            A TypeInfo object representing the parsed type

        """
        token = self.current_token

        # Handle end of input
        if token is None:
            raise ParseError("Unexpected end of input")

        # Handle open bracket (start of a tuple or list type)
        if token.type == TokenType.OPEN_BRACKET:
            return self.parse_tuple_type()

        # Handle identifier (simple type or start of generic type)
        if token.type == TokenType.IDENTIFIER:
            identifier = token.value
            self.next_token()  # Consume the identifier

            # Check if this is a generic type (followed by an open bracket)
            if (
                self.current_token is not None
                and self.current_token.type == TokenType.OPEN_BRACKET
            ):
                return self.parse_generic_type(identifier)

            # Otherwise, it's a simple type
            # Use the type name itself as the symbol_name
            return SimpleType(type_str=identifier, symbol_name=identifier)

        raise ParseError(f"Unexpected token: {token.type.name} '{token.value}'")

    def parse_generic_type(self, base_type_str: str) -> TypeInfo:
        """Parse a generic type (e.g., List[X], Dict[X, Y]).

        Args:
            base_type_str: The base type string (e.g., "List", "Dict")

        Returns:
            A GenericType representing the parsed type

        """
        # Create the base type with symbol name
        base_type = SimpleType(type_str=base_type_str, symbol_name=base_type_str)

        # Consume the open bracket
        self.expect_token_type(TokenType.OPEN_BRACKET)

        # Parse parameters
        parameters = []
        is_first_param = True

        while self.current_token is not None:
            # If we see a closing bracket and we've parsed at least one parameter
            # or we're parsing something like 'List[]', we're done
            if self.current_token.type == TokenType.CLOSE_BRACKET:
                self.next_token()  # Consume the closing bracket
                break

            # If this is not the first parameter, expect a comma
            if not is_first_param:
                self.expect_token_type(TokenType.COMMA)

            # Parse the parameter (which could be any type, including a union)
            parameter = self.parse_type()
            parameters.append(parameter)
            is_first_param = False

            # If we see a closing bracket, we're done
            if (
                self.current_token is not None
                and self.current_token.type == TokenType.CLOSE_BRACKET
            ):
                self.next_token()  # Consume the closing bracket
                break

        # Reconstruct the type string
        param_strs = [p.type_str for p in parameters]
        type_str = f"{base_type_str}[{', '.join(param_strs)}]"

        # Determine the kind based on the base type
        kind = TypeKind.GENERIC
        if base_type_str == "Union":
            kind = TypeKind.UNION
        elif base_type_str == "Optional":
            kind = TypeKind.OPTIONAL
        elif base_type_str == "Callable":
            kind = TypeKind.CALLABLE
            # Only validate that Callable has 2 parameters: args and return type
            if len(parameters) != CALLABLE_PARAMETER_LENGTH:
                raise ParseError(
                    f"Callable must have exactly 2 parameters, got {len(parameters)}"
                )
            # Note: We don't validate the first parameter's type anymore
            # It can be a tuple ([arg1, arg2]), a generic (ParamSpec), a type alias, etc.
        elif base_type_str == "Tuple":
            kind = TypeKind.TUPLE

        # Create and return the generic type
        return GenericType(
            type_str=type_str,
            base_type=base_type,
            parameters=parameters,
            kind=kind,
        )

    def parse_tuple_type(self) -> TypeInfo:
        """Parse a tuple type (e.g., [X, Y] for bare tuples).

        Returns:
            A GenericType representing the parsed tuple type

        """
        # Consume the open bracket
        self.expect_token_type(TokenType.OPEN_BRACKET)

        # Parse elements
        elements = []
        is_first_element = True

        while self.current_token is not None:
            # If we see a closing bracket, we're done
            if self.current_token.type == TokenType.CLOSE_BRACKET:
                self.next_token()  # Consume the closing bracket
                break

            # If this is not the first element, expect a comma
            if not is_first_element:
                self.expect_token_type(TokenType.COMMA)

            # Parse the element (which could be any type, including a union)
            element = self.parse_type()
            elements.append(element)
            is_first_element = False

            # If we see a closing bracket, we're done
            if (
                self.current_token is not None
                and self.current_token.type == TokenType.CLOSE_BRACKET
            ):
                self.next_token()  # Consume the closing bracket
                break

        # Reconstruct the type string
        element_strs = [e.type_str for e in elements]
        type_str = f"[{', '.join(element_strs)}]"

        # Create and return the tuple type (as a generic with TUPLE kind)
        base_type = SimpleType(type_str="tuple", symbol_name="tuple")
        return GenericType(
            type_str=type_str,
            base_type=base_type,
            parameters=elements,
            kind=TypeKind.TUPLE,
        )


def parse_type_string(type_str: str) -> TypeInfo:
    """Parse a type string into a TypeInfo object.

    Args:
        type_str: The type string to parse

    Returns:
        A TypeInfo object representing the parsed type

    Raises:
        ParseError: If the type string cannot be parsed into a valid type

    """
    # Pre-check for unbalanced brackets before tokenizing
    open_count = type_str.count("[")
    close_count = type_str.count("]")
    if open_count != close_count:
        raise ParseError(f"Unbalanced brackets in type string: '{type_str}'")

    try:
        tokens = tokenize(type_str)
        parser = Parser(tokens=tokens)
        return parser.parse()
    except Exception as e:
        # Wrap any exceptions in a ParseError
        if not isinstance(e, ParseError):
            e = ParseError(f"Error parsing type string '{type_str}': {e!s}")
        raise e
