import sys
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
# from src.compiler import Compiler  

def interpret(filename):
    if not filename.endswith(".xn"):
        print("Error: Expected a file with .xn extension.")
        sys.exit(1)
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    lexer = Lexer(code)
    tokens = lexer.lex_analysis()

    parser = Parser(tokens)
    root_node = parser.parse()

    interpreter = Interpreter()
    interpreter.interpret(root_node)

def compile_code():
    print("🔧 Compilation not implemented yet.")

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "-i":
        filename = sys.argv[2]
        interpret(filename)
    elif len(sys.argv) == 1:
        compile_code()
    else:
        print("Usage:")
        print("  Interpret: python main.py -i <filename.xn>")
        print("  Compile:   python main.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
