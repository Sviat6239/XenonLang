from src.lexer import Lexer
from src.parser import Parser


code = '''
print("Hello from Xenon!");
'''

lexer = Lexer(code)
lexer.lex_analysis() 

parser = Parser(lexer.token_list)
root_node = parser.parse_code()
parser.run(root_node)
