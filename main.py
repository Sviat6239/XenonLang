from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter

def main():
    code = '''
    for (var i = 0; i < 72 + 1; i = i + 1) {
        if (i % 2 == 0) {
            print("Even number: " + i);
        } else {
            print("Odd number: " + i);
        }
    }
    '''
    
    lexer = Lexer(code)
    tokens = lexer.lex_analysis()
    
    parser = Parser(tokens)
    root_node = parser.parse()
    
    interpreter = Interpreter()
    interpreter.interpret(root_node)

if __name__ == "__main__":
    main()