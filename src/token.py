class TokenType:
    def __init__(self, name: str, regex: str):
        self.name = name
        self.regex = regex

    def __repr__(self):
        return f"TokenType(name='{self.name}', regex=r'{self.regex}')"


class Token:
    def __init__(self, type: TokenType, value: str, position: int):
        self.type = type
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token(type={self.type.name}, value='{self.value}', pos={self.position})"


token_types_list = {
    # Литералы
    'NUMBER': TokenType("NUMBER", r'\d+(\.\d+)?'), 
    'STRING': TokenType("STRING", r'(\"[^\"\n]*\"|\'[^\'\n]*\')'),
    'VARIABLE': TokenType("VARIABLE", r'[a-zA-Z_][a-zA-Z0-9_]*'), 

    # Операторы
    'ASSIGN': TokenType("ASSIGN", r'='),
    'EQUAL': TokenType("EQUAL", r'=='),
    'NOT_EQUAL': TokenType("NOT_EQUAL", r'!='),
    'LESS': TokenType("LESS", r'<'),
    'GREATER': TokenType("GREATER", r'>'),
    'LESS_EQUAL': TokenType("LESS_EQUAL", r'<='),
    'GREATER_EQUAL': TokenType("GREATER_EQUAL", r'>='),

    'PLUS': TokenType("PLUS", r'\+'),
    'MINUS': TokenType("MINUS", r'-'),
    'MULTIPLY': TokenType("MULTIPLY", r'\*'),
    'DIVIDE': TokenType("DIVIDE", r'/'),
    'MODULO': TokenType("MODULO", r'%'),

    # Разделители
    'SEMICOLON': TokenType("SEMICOLON", r';'),
    'COLON': TokenType("COLON", r':'),
    'COMMA': TokenType("COMMA", r','),
    'DOT': TokenType("DOT", r'\.'),

    # Скобки
    'LPAREN': TokenType("LPAREN", r'\('),
    'RPAREN': TokenType("RPAREN", r'\)'),
    'LBRACE': TokenType("LBRACE", r'\{'),
    'RBRACE': TokenType("RBRACE", r'\}'),
    'LBRACKET': TokenType("LBRACKET", r'\['),
    'RBRACKET': TokenType("RBRACKET", r'\]'),

    # Ключевые слова
    'IF': TokenType("IF", r'\bif\b'),
    'ELSE': TokenType("ELSE", r'\belse\b'),
    'WHILE': TokenType("WHILE", r'\bwhile\b'),
    'FOR': TokenType("FOR", r'\bfor\b'),
    'RETURN': TokenType("RETURN", r'\breturn\b'),
    'FUNCTION': TokenType("FUNCTION", r'\bfun\b'),
    'PRINT': TokenType("PRINT", r'\bprint\b'),
    'TRUE': TokenType("TRUE", r'\btrue\b'),
    'FALSE': TokenType("FALSE", r'\bfalse\b'),
    'NULL': TokenType("NULL", r'\bnull\b'),

    # Пробелы и комментарии
    'SPACE': TokenType("SPACE", r'[ \n\t\r]+'),
    'COMMENT': TokenType("COMMENT", r'//[^\n]*'), 
}

