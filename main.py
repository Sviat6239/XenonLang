from src.lexer import Lexer
from src.parser import Parser


code = '''
hello = "Hello,";
world = "world!";
print(hello + world);
'''

lexer = Lexer(code)
lexer.lex_analysis() 

parser = Parser(lexer.token_list)
root_node = parser.parse_code()
parser.run(root_node)
