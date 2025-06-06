class TokenType:
    def __init__(self, name: str, regex: str):
        self.name = name
        self.regex = regex

    def __repr__(self):
        return f"TokenType(name='{self.name}', regex=r'{self.regex}')"


class Token:
    def __init__(self, type: TokenType, value: str, position: int, line: int = 1, column: int = 1):
        self.type = type
        self.value = value
        self.position = position
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token(type={self.type.name}, value='{self.value}', pos={self.position}, line={self.line}, col={self.column})"

token_types_list = {
    # Literals
    'NUMBER': TokenType("NUMBER", r'-?\d+(\.\d+)?([eE][+-]?\d+)?'),  # Integers, decimals, scientific notation
    'STRING': TokenType("STRING", r'\"[^\"\n]*\"|\'[^\'\n]*\''),  # Double or single-quoted strings
    'CHAR': TokenType("CHAR", r'\'[^\']?\''),  # Single character literals
    'VARIABLE': TokenType("VARIABLE", r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),  # Identifiers
    'TRUE': TokenType("TRUE", r'\btrue\b'),  # Boolean true
    'FALSE': TokenType("FALSE", r'\bfalse\b'),  # Boolean false
    'NULL': TokenType("NULL", r'\bnull\b'),  # Null literal

    # Operators
    'ASSIGN': TokenType("ASSIGN", r'='),  # Assignment
    'EQUAL': TokenType("EQUAL", r'=='),  # Equality comparison
    'NOT_EQUAL': TokenType("NOT_EQUAL", r'!='),  # Inequality comparison
    'LESS': TokenType("LESS", r'<'),  # Less than
    'GREATER': TokenType("GREATER", r'>'),  # Greater than
    'LESS_EQUAL': TokenType("LESS_EQUAL", r'<='),  # Less than or equal
    'GREATER_EQUAL': TokenType("GREATER_EQUAL", r'>='),  # Greater than or equal
    'PLUS': TokenType("PLUS", r'\+'),  # Addition
    'MINUS': TokenType("MINUS", r'-'),  # Subtraction
    'MULTIPLY': TokenType("MULTIPLY", r'\*'),  # Multiplication
    'DIVIDE': TokenType("DIVIDE", r'/'),  # Division
    'MODULO': TokenType("MODULO", r'%'),  # Modulo
    'AND': TokenType("AND", r'&&'),  # Logical AND
    'OR': TokenType("OR", r'\|\|'),  # Logical OR
    'NOT': TokenType("NOT", r'!'),  # Logical NOT
    'BIT_AND': TokenType("BIT_AND", r'&'),  # Bitwise AND
    'BIT_OR': TokenType("BIT_OR", r'\|'),  # Bitwise OR
    'BIT_XOR': TokenType("BIT_XOR", r'\^'),  # Bitwise XOR
    'BIT_NOT': TokenType("BIT_NOT", r'~'),  # Bitwise NOT
    'SHL': TokenType("SHL", r'<<'),  # Shift left
    'SHR': TokenType("SHR", r'>>'),  # Shift right
    'NULL_COALESCE': TokenType("NULL_COALESCE", r'\?\?'),  # Null coalescing
    'ELVIS': TokenType("ELVIS", r'\?:'),  # Elvis operator
    'INCREMENT': TokenType("INCREMENT", r'\+\+'),  # Increment
    'DECREMENT': TokenType("DECREMENT", r'--'),  # Decrement

    # Delimiters
    'SEMICOLON': TokenType("SEMICOLON", r';'),  # Statement terminator
    'COLON': TokenType("COLON", r':'),  # Type annotations
    'COMMA': TokenType("COMMA", r','),  # Separator
    'DOT': TokenType("DOT", r'\.'),  # Member access
    'ARROW': TokenType("ARROW", r'->'),  # Lambda or function types

    # Brackets
    'LPAREN': TokenType("LPAREN", r'\('),  # Left parenthesis
    'RPAREN': TokenType("RPAREN", r'\)'),  # Right parenthesis
    'LBRACE': TokenType("LBRACE", r'\{'),  # Left brace
    'RBRACE': TokenType("RBRACE", r'\}'),  # Right brace
    'LBRACKET': TokenType("LBRACKET", r'\['),  # Left bracket
    'RBRACKET': TokenType("RBRACKET", r'\]'),  # Right bracket

    # Keywords (Control Flow)
    'IF': TokenType("IF", r'\bif\b'),  # If statement
    'ELSE': TokenType("ELSE", r'\belse\b'),  # Else statement
    'WHILE': TokenType("WHILE", r'\bwhile\b'),  # While loop
    'FOR': TokenType("FOR", r'\bfor\b'),  # For loop
    'DO': TokenType("DO", r'\bdo\b'),  # Do-while loop
    'SWITCH': TokenType("SWITCH", r'\bswitch\b'),  # Switch statement
    'CASE': TokenType("CASE", r'\bcase\b'),  # Case in switch
    'DEFAULT': TokenType("DEFAULT", r'\bdefault\b'),  # Default in switch
    'BREAK': TokenType("BREAK", r'\bbreak\b'),  # Break statement
    'CONTINUE': TokenType("CONTINUE", r'\bcontinue\b'),  # Continue statement
    'RETURN': TokenType("RETURN", r'\breturn\b'),  # Return statement
    'TRY': TokenType("TRY", r'\btry\b'),  # Try block
    'CATCH': TokenType("CATCH", r'\bcatch\b'),  # Catch block
    'FINALLY': TokenType("FINALLY", r'\bfinally\b'),  # Finally block
    'THROW': TokenType("THROW", r'\bthrow\b'),  # Throw exception

    # Keywords (Definitions)
    'PRINT': TokenType("PRINT", r'\bprint\b'),  # Print function
    'FUNCTION': TokenType("FUNCTION", r'\bfun\b'),  # Function definition
    'CLASS': TokenType("CLASS", r'\bclass\b'),  # Class definition
    'INTERFACE': TokenType("INTERFACE", r'\binterface\b'),  # Interface definition
    'ENUM': TokenType("ENUM", r'\benum\b'),  # Enum definition
    'VAR': TokenType("VAR", r'\bvar\b'),  # Variable declaration
    'VAL': TokenType("VAL", r'\bval\b'),  # Immutable variable
    'CONST': TokenType("CONST", r'\bconst\b'),  # Constant declaration
    'STATIC': TokenType("STATIC", r'\bstatic\b'),  # Static member
    'NEW': TokenType("NEW", r'\bnew\b'),  # Object instantiation

    # Access Modifiers
    'PUBLIC': TokenType("PUBLIC", r'\bpublic\b'),  # Public access
    'PRIVATE': TokenType("PRIVATE", r'\bprivate\b'),  # Private access
    'PROTECTED': TokenType("PROTECTED", r'\bprotected\b'),  # Protected access
    'INTERNAL': TokenType("INTERNAL", r'\binternal\b'),  # Internal access

    # Type Declarations
    'INT': TokenType("INT", r'\bint\b'),  # Integer type
    'FLOAT': TokenType("FLOAT", r'\bfloat\b'),  # Float type
    'DOUBLE': TokenType("DOUBLE", r'\bdouble\b'),  # Double type
    'BOOLEAN': TokenType("BOOLEAN", r'\bboolean\b'),  # Boolean type
    'STRING_TYPE': TokenType("STRING_TYPE", r'\bstring\b'),  # String type
    'VOID': TokenType("VOID", r'\bvoid\b'),  # Void type
    'ANY': TokenType("ANY", r'\bany\b'),  # Any type
    'NULLABLE': TokenType("NULLABLE", r'\?'),  # Nullable type modifier

    # Other Keywords
    'IMPORT': TokenType("IMPORT", r'\bimport\b'),  # Import statement
    'FROM': TokenType("FROM", r'\bfrom\b'),  # From clause for imports
    'AS': TokenType("AS", r'\bas\b'),  # Alias for imports
    'THIS': TokenType("THIS", r'\bthis\b'),  # This reference
    'SUPER': TokenType("SUPER", r'\bsuper\b'),  # Super reference
    'INSTANCEOF': TokenType("INSTANCEOF", r'\binstanceof\b'),  # Instanceof operator
    'LAMBDA': TokenType("LAMBDA", r'\blambda\b'),  # Lambda expression

    # Whitespace and Comments
    'SPACE': TokenType("SPACE", r'[ \n\t\r]+'),  # Whitespace
    'COMMENT': TokenType("COMMENT", r'#.*'),  # Python-style single-line comment
}