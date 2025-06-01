import re
from .token import Token, TokenType, token_types_list


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.token_list: list[Token] = []

    def lex_analysis(self) -> list[Token]:
        while self.next_token():
            pass
        self.token_list = [
            token for token in self.token_list
            if token.type.name != token_types_list['SPACE'].name
        ]
        return self.token_list

    def next_token(self) -> bool:
        if self.pos >= len(self.code):
            return False

        for token_type in token_types_list.values():
            pattern = re.compile(r'^' + token_type.regex)
            match = pattern.match(self.code[self.pos:])
            if match:
                value = match.group(0)
                token = Token(token_type, value, self.pos)
                self.token_list.append(token)
                self.pos += len(value)
                return True

        raise SyntaxError(f"Error at {self.pos}")
