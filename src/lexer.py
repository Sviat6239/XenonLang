import re
from typing import List
from .token import Token, TokenType, token_types_list

class Lexer:
    """Tokenizes source code into a list of Tokens for a strongly-typed language with Python-like imports."""
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.token_list: List[Token] = []
        # Token order prioritizes multi-char operators, keywords, then VARIABLE
        self.token_order = [
            # Multi-character operators (must come first)
            'EQUAL', 'NOT_EQUAL', 'LESS_EQUAL', 'GREATER_EQUAL', 'NULL_COALESCE', 
            'ELVIS', 'INCREMENT', 'DECREMENT', 'AND', 'OR', 'SHL', 'SHR',
            'BIT_AND', 'BIT_OR', 'BIT_XOR',
            # Keywords
            'IF', 'ELSE', 'WHILE', 'FOR', 'DO', 'SWITCH', 'CASE', 'DEFAULT',
            'BREAK', 'CONTINUE', 'RETURN', 'TRY', 'CATCH', 'FINALLY', 'THROW',
            'FUNCTION', 'CLASS', 'INTERFACE', 'ENUM', 'VAR', 'VAL', 'CONST',
            'STATIC', 'PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL', 'NEW',
            'THIS', 'SUPER', 'INSTANCEOF', 'LAMBDA', 'IMPORT', 'FROM', 'AS',
            'TRUE', 'FALSE', 'NULL', 'PRINT',
            # Types
            'INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'VOID', 'ANY',
            # Literals
            'NUMBER', 'STRING', 'CHAR',
            # Single-character operators and delimiters
            'ASSIGN', 'LESS', 'GREATER', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE',
            'MODULO', 'NOT', 'BIT_NOT', 'SEMICOLON', 'COLON', 'COMMA', 'DOT',
            'ARROW', 'NULLABLE',
            # Brackets
            'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
            # Whitespace and comments
            'SPACE', 'COMMENT',
            # Identifiers (last to avoid matching keywords as variables)
            'VARIABLE'
        ]
        # Compile regex patterns for each token type
        self.compiled_token_types = [
            (token_types_list[name], re.compile(r'^' + token_types_list[name].regex))
            for name in self.token_order
            if name in token_types_list  # Ensure token exists
        ]

    def update_position(self, value: str):
        """Updates line and column numbers based on the token value."""
        for char in value:
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        self.pos += len(value)

    def lex_analysis(self) -> List[Token]:
        """Performs lexical analysis, returning a list of tokens excluding SPACE and COMMENT."""
        while self.next_token():
            pass
        # Filter out whitespace and comments
        self.token_list = [
            token for token in self.token_list
            if token.type.name not in ('SPACE', 'COMMENT')
        ]
        return self.token_list

    def next_token(self) -> bool:
        """Attempts to match the next token from the current position."""
        if self.pos >= len(self.code):
            return False

        substring = self.code[self.pos:]
        for token_type, pattern in self.compiled_token_types:
            match = pattern.match(substring)
            if match:
                value = match.group(0)
                # Store line and column before updating position
                token = Token(token_type, value, self.pos, self.line, self.column)
                self.token_list.append(token)
                # Update position, accounting for newlines in comments
                self.update_position(value)
                return True

        # Provide detailed error for invalid characters
        char = self.code[self.pos] if self.pos < len(self.code) else 'EOF'
        raise SyntaxError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")