from abc import ABC
from typing import List, Optional, Any, Dict
from .token import Token, TokenType, token_types_list
from .ast import *

class Parser:
    """Parses a list of tokens into an AST for a strongly-typed language with Python-like imports."""
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token: Optional[Token] = tokens[0] if tokens else None

    def advance(self):
        """Advances to the next token."""
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def expect(self, token_type_name: str) -> Token:
        """Expects a token of the given type, advances, and returns it; raises SyntaxError if not found."""
        if self.current_token and self.current_token.type.name == token_type_name:
            token = self.current_token
            self.advance()
            return token
        raise SyntaxError(f"Expected {token_type_name}, got {self.current_token.type.name if self.current_token else 'EOF'} at position {self.current_token.position if self.current_token else 'EOF'}")

    def parse(self) -> ProgramNode:
        """Parses the entire program into a ProgramNode with imports and statements."""
        return self.parse_program()

    def parse_program(self) -> ProgramNode:
        """Parses imports and statements into a ProgramNode.

        Example:
            import math;
            from os import path as ospath;
            var x: int = 5;
        """
        imports = []
        statements = []
        while self.current_token:
            if self.current_token.type.name == 'IMPORT':
                imports.append(self.parse_import())
            else:
                statements.append(self.parse_statement())
        return ProgramNode(imports, statements)

    def parse_import(self) -> ImportNode:
        """Parses Python-style imports (e.g., 'import math;', 'from os import path as ospath;').

        Example:
            import math;                 // ImportNode(module=['math'], names=[], alias=None)
            from os import path as ospath; // ImportNode(module=['os', 'path'], names=['path'], alias='ospath')
        """
        self.expect('IMPORT')
        module = [self.expect('VARIABLE')]
        while self.current_token and self.current_token.type.name == 'DOT':
            self.advance()
            module.append(self.expect('VARIABLE'))
        names = []
        alias = None
        if self.current_token and self.current_token.type.name == 'FROM':
            self.advance()
            names = [self.expect('VARIABLE')]
            while self.current_token and self.current_token.type.name == 'COMMA':
                self.advance()
                names.append(self.expect('VARIABLE'))
            if self.current_token and self.current_token.type.name == 'AS':
                self.advance()
                alias = self.expect('VARIABLE')
        elif self.current_token and self.current_token.type.name == 'AS':
            self.advance()
            alias = self.expect('VARIABLE')
        self.expect('SEMICOLON')
        return ImportNode(module, names, alias)

    def parse_statement(self) -> ExpressionNode:
        """Parses a single statement (e.g., declaration, control flow, expression)."""
        if not self.current_token:
            raise SyntaxError("Unexpected end of input")
        
        if self.current_token.type.name in ('VAR', 'VAL', 'CONST'):
            return self.parse_declaration()
        elif self.current_token.type.name == 'IF':
            return self.parse_if_statement()
        elif self.current_token.type.name == 'WHILE':
            return self.parse_while_statement()
        elif self.current_token.type.name == 'DO':
            return self.parse_do_while_statement()
        elif self.current_token.type.name == 'FOR':
            return self.parse_for_statement()
        elif self.current_token.type.name == 'SWITCH':
            return self.parse_switch_statement()
        elif self.current_token.type.name == 'TRY':
            return self.parse_try_statement()
        elif self.current_token.type.name == 'THROW':
            return self.parse_throw_statement()
        elif self.current_token.type.name == 'FUNCTION':
            return self.parse_function_def()
        elif self.current_token.type.name == 'CLASS':
            return self.parse_class_def()
        elif self.current_token.type.name == 'INTERFACE':
            return self.parse_interface_def()
        elif self.current_token.type.name == 'ENUM':
            return self.parse_enum_def()
        elif self.current_token.type.name == 'RETURN':
            return self.parse_return_statement()
        elif self.current_token.type.name == 'BREAK':
            self.advance()
            self.expect('SEMICOLON')
            return BreakNode()
        elif self.current_token.type.name == 'CONTINUE':
            self.advance()
            self.expect('SEMICOLON')
            return ContinueNode()
        elif self.current_token.type.name == 'PRINT':
            return self.parse_print_statement()
        elif self.current_token.type.name == 'LBRACE':
            return self.parse_block()
        else:
            expr = self.parse_expression()
            self.expect('SEMICOLON')
            return expr

    def parse_declaration(self) -> ExpressionNode:
        """Parses variable declarations (var, val, const) with optional type annotations.

        Example:
            var x: int = 5;     // VarDeclarationNode(var_token, VariableNode('x'), Token('INT'), NumberNode('5'))
            val y: string = "hi"; // ValDeclarationNode(val_token, VariableNode('y'), Token('STRING_TYPE'), StringNode('"hi"'))
            const z: int = 10;   // ConstDeclarationNode(const_token, VariableNode('z'), Token('INT'), NumberNode('10'))
        """
        decl_type = self.current_token.type.name
        decl_token = self.expect(decl_type)
        variable = VariableNode(self.expect('VARIABLE'))
        type_token = None
        if self.current_token and self.current_token.type.name == 'COLON':
            self.advance()
            type_token = self.expect_one_of(('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'VOID', 'ANY', 'VARIABLE'))
            if self.current_token and self.current_token.type.name == 'NULLABLE':
                self.advance()  # Consume '?' for nullable types
        expr = None
        if self.current_token and self.current_token.type.name == 'ASSIGN':
            self.advance()
            expr = self.parse_expression()
        self.expect('SEMICOLON')
        if decl_type == 'VAR':
            return VarDeclarationNode(decl_token, variable, type_token, expr)
        elif decl_type == 'VAL':
            if not expr:
                raise SyntaxError("Val declaration requires an initializer")
            return ValDeclarationNode(decl_token, variable, type_token, expr)
        else:  # CONST
            if not expr:
                raise SyntaxError("Const declaration requires an initializer")
            return ConstDeclarationNode(decl_token, variable, type_token, expr)

    def expect_one_of(self, token_type_names: tuple) -> Token:
        """Expects one of the specified token types."""
        if self.current_token and self.current_token.type.name in token_type_names:
            token = self.current_token
            self.advance()
            return token
        raise SyntaxError(f"Expected one of {token_type_names}, got {self.current_token.type.name if self.current_token else 'EOF'}")

    def parse_if_statement(self) -> IfNode:
        """Parses an if statement with optional else branch.

        Example:
            if (x > 0) { return 1; } else { return 0; }
        """
        self.expect('IF')
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        then_branch = self.parse_block()
        else_branch = None
        if self.current_token and self.current_token.type.name == 'ELSE':
            self.advance()
            else_branch = self.parse_block()
        return IfNode(condition, then_branch, else_branch)

    def parse_while_statement(self) -> WhileNode:
        """Parses a while loop.

        Example:
            while (x < 10) { x = x + 1; }
        """
        self.expect('WHILE')
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_do_while_statement(self) -> DoWhileNode:
        """Parses a do-while loop.

        Example:
            do { x = x + 1; } while (x < 10);
        """
        self.expect('DO')
        body = self.parse_block()
        self.expect('WHILE')
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        return DoWhileNode(body, condition)

    def parse_for_statement(self) -> ForNode:
        """Parses a for loop with optional init, condition, and step.

        Example:
            for (var i: int = 0; i < 10; i++) { print(i); }
        """
        self.expect('FOR')
        self.expect('LPAREN')
        init = self.parse_statement() if self.current_token and self.current_token.type.name != 'SEMICOLON' else None
        if self.current_token and self.current_token.type.name == 'SEMICOLON':
            self.advance()
        cond = self.parse_expression() if self.current_token and self.current_token.type.name != 'SEMICOLON' else None
        self.expect('SEMICOLON')
        step = self.parse_expression() if self.current_token and self.current_token.type.name != 'RPAREN' else None
        self.expect('RPAREN')
        body = self.parse_block()
        return ForNode(init, cond, step, body)

    def parse_switch_statement(self) -> SwitchNode:
        """Parses a switch statement with cases and optional default.

        Example:
            switch (x) { case 1: { print("one"); break; } default: { print("other"); } }
        """
        self.expect('SWITCH')
        self.expect('LPAREN')
        expression = self.parse_expression()
        self.expect('RPAREN')
        self.expect('LBRACE')
        cases = []
        default = None
        while self.current_token and self.current_token.type.name != 'RBRACE':
            if self.current_token.type.name == 'CASE':
                self.advance()
                value = self.parse_expression()
                self.expect('COLON')
                body = self.parse_block()
                cases.append(CaseNode(value, body))
            elif self.current_token.type.name == 'DEFAULT':
                self.advance()
                self.expect('COLON')
                default = self.parse_block()
        self.expect('RBRACE')
        return SwitchNode(expression, cases, default)

    def parse_try_statement(self) -> TryNode:
        """Parses a try-catch-finally block.

        Example:
            try { throw "error"; } catch (e: string) { print(e); } finally { print("done"); }
        """
        self.expect('TRY')
        try_block = self.parse_block()
        catches = []
        while self.current_token and self.current_token.type.name == 'CATCH':
            self.advance()
            self.expect('LPAREN')
            exception_var = VariableNode(self.expect('VARIABLE'))
            type_token = None
            if self.current_token and self.current_token.type.name == 'COLON':
                self.advance()
                type_token = self.expect_one_of(('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'ANY', 'VARIABLE'))
            self.expect('RPAREN')
            body = self.parse_block()
            catches.append(CatchNode(exception_var, type_token, body))
        finally_block = None
        if self.current_token and self.current_token.type.name == 'FINALLY':
            self.advance()
            finally_block = self.parse_block()
        return TryNode(try_block, catches, finally_block)

    def parse_throw_statement(self) -> ThrowNode:
        """Parses a throw statement.

        Example:
            throw "error";
        """
        self.expect('THROW')
        expr = self.parse_expression()
        self.expect('SEMICOLON')
        return ThrowNode(expr)

    def parse_function_def(self) -> FunctionDefNode:
        """Parses a function definition with modifiers, parameters, and return type.

        Example:
            public fun add(x: int, y: int?): int { return x + y; }
        """
        modifiers = []
        while self.current_token and self.current_token.type.name in ('PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL', 'STATIC'):
            modifiers.append(self.current_token)
            self.advance()
        self.expect('FUNCTION')
        name = self.expect('VARIABLE')
        self.expect('LPAREN')
        params = []
        if self.current_token and self.current_token.type.name != 'RPAREN':
            params.append(self.parse_param())
            while self.current_token and self.current_token.type.name == 'COMMA':
                self.advance()
                params.append(self.parse_param())
        self.expect('RPAREN')
        return_type = None
        if self.current_token and self.current_token.type.name == 'COLON':
            self.advance()
            return_type = self.expect_one_of(('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'VOID', 'ANY', 'VARIABLE'))
            if self.current_token and self.current_token.type.name == 'NULLABLE':
                self.advance()
        body = self.parse_block()
        return FunctionDefNode(name, params, return_type, body, modifiers)

    def parse_param(self) -> ParamNode:
        """Parses a function parameter with optional type and nullability.

        Example:
            x: int?     // ParamNode(name='x', type_token=Token('INT'), is_nullable=True)
        """
        name = self.expect('VARIABLE')
        type_token = None
        is_nullable = False
        if self.current_token and self.current_token.type.name == 'COLON':
            self.advance()
            type_token = self.expect_one_of(('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'ANY', 'VARIABLE'))
            if self.current_token and self.current_token.type.name == 'NULLABLE':
                self.advance()
                is_nullable = True
        return ParamNode(name, type_token, is_nullable)

    def parse_class_def(self) -> ClassNode:
        """Parses a class definition with optional superclass and interfaces.

        Example:
            public class MyClass : SuperClass { var x: int = 0; }
        """
        modifiers = []
        while self.current_token and self.current_token.type.name in ('PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL'):
            modifiers.append(self.current_token)
            self.advance()
        self.expect('CLASS')
        name = self.expect('VARIABLE')
        superclass = None
        interfaces = []
        if self.current_token and self.current_token.type.name == 'COLON':
            self.advance()
            superclass = VariableNode(self.expect('VARIABLE'))
            while self.current_token and self.current_token.type.name == 'COMMA':
                self.advance()
                interfaces.append(VariableNode(self.expect('VARIABLE')))
        self.expect('LBRACE')
        members = []
        while self.current_token and self.current_token.type.name != 'RBRACE':
            members.append(self.parse_statement())
        self.expect('RBRACE')
        return ClassNode(name, superclass, interfaces, members, modifiers)

    def parse_interface_def(self) -> InterfaceNode:
        """Parses an interface definition.

        Example:
            interface MyInterface { fun method(): void; }
        """
        modifiers = []
        while self.current_token and self.current_token.type.name in ('PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL'):
            modifiers.append(self.current_token)
            self.advance()
        self.expect('INTERFACE')
        name = self.expect('VARIABLE')
        self.expect('LBRACE')
        members = []
        while self.current_token and self.current_token.type.name != 'RBRACE':
            members.append(self.parse_statement())
        self.expect('RBRACE')
        return InterfaceNode(name, members, modifiers)

    def parse_enum_def(self) -> EnumNode:
        """Parses an enum definition.

        Example:
            enum Color { RED, GREEN }
        """
        self.expect('ENUM')
        name = self.expect('VARIABLE')
        self.expect('LBRACE')
        values = []
        members = []
        while self.current_token and self.current_token.type.name != 'RBRACE':
            if self.current_token.type.name == 'VARIABLE':
                values.append(self.current_token)
                self.advance()
                if self.current_token and self.current_token.type.name == 'COMMA':
                    self.advance()
            else:
                members.append(self.parse_statement())
        self.expect('RBRACE')
        return EnumNode(name, values, members)

    def parse_return_statement(self) -> ReturnNode:
        """Parses a return statement.

        Example:
            return x + 1;
        """
        self.expect('RETURN')
        expr = self.parse_expression() if self.current_token and self.current_token.type.name != 'SEMICOLON' else None
        self.expect('SEMICOLON')
        return ReturnNode(expr)

    def parse_print_statement(self) -> PrintNode:
        """Parses a print statement.

        Example:
            print(x);
        """
        self.expect('PRINT')
        self.expect('LPAREN')
        expr = self.parse_expression()
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        return PrintNode(expr)

    def parse_block(self) -> BlockNode:
        """Parses a block of statements within braces.

        Example:
            { var x: int = 5; print(x); }
        """
        self.expect('LBRACE')
        statements = []
        while self.current_token and self.current_token.type.name != 'RBRACE':
            statements.append(self.parse_statement())
        self.expect('RBRACE')
        return BlockNode(statements)

    def parse_expression(self) -> ExpressionNode:
        """Parses an expression, starting with the highest precedence."""
        return self.parse_null_coalesce()

    def parse_null_coalesce(self) -> ExpressionNode:
        """Parses null-coalescing expressions (??).

        Example:
            x ?? 0
        """
        expr = self.parse_elvis()
        while self.current_token and self.current_token.type.name == 'NULL_COALESCE':
            self.advance()
            right = self.parse_elvis()
            expr = NullCoalesceNode(expr, right)
        return expr

    def parse_elvis(self) -> ExpressionNode:
        """Parses Elvis operator expressions (?:).

        Example:
            x ?: 0
        """
        expr = self.parse_assignment()
        while self.current_token and self.current_token.type.name == 'ELVIS':
            self.advance()
            right = self.parse_assignment()
            expr = ElvisNode(expr, right)
        return expr

    def parse_assignment(self) -> ExpressionNode:
        """Parses assignment expressions."""
        expr = self.parse_equality()
        if self.current_token and self.current_token.type.name == 'ASSIGN':
            token = self.current_token
            self.advance()
            if not isinstance(expr, VariableNode):
                raise SyntaxError(f"Invalid assignment target at position {token.position}")
            value = self.parse_expression()
            return AssignNode(token, expr, value)
        return expr

    def parse_equality(self) -> ExpressionNode:
        """Parses equality comparisons (==, !=)."""
        expr = self.parse_comparison()
        while self.current_token and self.current_token.type.name in ('EQUAL', 'NOT_EQUAL'):
            token = self.current_token
            self.advance()
            right = self.parse_comparison()
            expr = BinaryOperationNode(token, expr, right)
        return expr

    def parse_comparison(self) -> ExpressionNode:
        """Parses comparison operations (<, >, <=, >=)."""
        expr = self.parse_term()
        while self.current_token and self.current_token.type.name in ('LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL'):
            token = self.current_token
            self.advance()
            right = self.parse_term()
            expr = BinaryOperationNode(token, expr, right)
        return expr

    def parse_term(self) -> ExpressionNode:
        """Parses addition and subtraction (+, -)."""
        expr = self.parse_factor()
        while self.current_token and self.current_token.type.name in ('PLUS', 'MINUS'):
            token = self.current_token
            self.advance()
            right = self.parse_factor()
            expr = BinaryOperationNode(token, expr, right)
        return expr

    def parse_factor(self) -> ExpressionNode:
        """Parses multiplication, division, and modulo (*, /, %)."""
        expr = self.parse_unary()
        while self.current_token and self.current_token.type.name in ('MULTIPLY', 'DIVIDE', 'MODULO'):
            token = self.current_token
            self.advance()
            right = self.parse_unary()
            expr = BinaryOperationNode(token, expr, right)
        return expr

    def parse_unary(self) -> ExpressionNode:
        """Parses unary operations (-, !, ~)."""
        if self.current_token and self.current_token.type.name in ('MINUS', 'NOT', 'BIT_NOT'):
            token = self.current_token
            self.advance()
            operand = self.parse_unary()
            return UnaryOperationNode(token, operand)
        return self.parse_instanceof()

    def parse_instanceof(self) -> ExpressionNode:
        """Parses instanceof expressions.

        Example:
            x instanceof int
        """
        expr = self.parse_new()
        if self.current_token and self.current_token.type.name == 'INSTANCEOF':
            self.advance()
            type_token = self.expect_one_of(('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'ANY', 'VARIABLE'))
            return InstanceOfNode(expr, type_token)
        return expr

    def parse_new(self) -> ExpressionNode:
        """Parses object instantiation with 'new'.

        Example:
            new MyClass(1, 2)
        """
        if self.current_token and self.current_token.type.name == 'NEW':
            self.advance()
            type_token = self.expect('VARIABLE')
            self.expect('LPAREN')
            args = []
            if self.current_token and self.current_token.type.name != 'RPAREN':
                args.append(self.parse_expression())
                while self.current_token and self.current_token.type.name == 'COMMA':
                    self.advance()
                    args.append(self.parse_expression())
            self.expect('RPAREN')
            return NewNode(type_token, args)
        return self.parse_lambda()

    def parse_lambda(self) -> ExpressionNode:
        """Parses lambda expressions.

        Example:
            lambda (x: int) -> x + 1
        """
        if self.current_token and self.current_token.type.name == 'LAMBDA':
            self.advance()
            self.expect('LPAREN')
            params = []
            if self.current_token and self.current_token.type.name != 'RPAREN':
                params.append(self.parse_param())
                while self.current_token and self.current_token.type.name == 'COMMA':
                    self.advance()
                    params.append(self.parse_param())
            self.expect('RPAREN')
            self.expect('ARROW')
            body = self.parse_expression()
            return LambdaNode(params, body)
        return self.parse_primary()

    def parse_primary(self) -> ExpressionNode:
        """Parses primary expressions (literals, variables, function calls, parenthesized expressions)."""
        if not self.current_token:
            raise SyntaxError("Expected expression, got EOF")
        
        token = self.current_token
        self.advance()

        if token.type.name == 'NUMBER':
            return NumberNode(token)
        elif token.type.name == 'STRING':
            return StringNode(token)
        elif token.type.name == 'CHAR':
            return CharNode(token)
        elif token.type.name in ('TRUE', 'FALSE'):
            return BooleanNode(token)
        elif token.type.name == 'NULL':
            return NullNode(token)
        elif token.type.name == 'VARIABLE':
            keyword_values = {
                'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'default', 'return', 'fun',
                'class', 'interface', 'enum', 'var', 'val', 'const', 'break', 'continue',
                'try', 'catch', 'finally', 'throw', 'true', 'false', 'null', 'public',
                'private', 'protected', 'internal', 'static', 'new', 'this', 'super',
                'instanceof', 'lambda', 'import', 'from', 'as', 'print'
            }
            if token.value.lower() in keyword_values:
                raise SyntaxError(f"Unexpected keyword '{token.value}' used as variable at position {token.position}")
            if self.current_token and self.current_token.type.name == 'LPAREN':
                return self.parse_function_call(token)
            return VariableNode(token)
        elif token.type.name == 'LPAREN':
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected token {token.type.name} at position {token.position}")

    def parse_function_call(self, func_token: Token) -> FunctionCallNode:
        """Parses a function call.

        Example:
            foo(1, "hello")
        """
        self.expect('LPAREN')
        args = []
        if self.current_token and self.current_token.type.name != 'RPAREN':
            args.append(self.parse_expression())
            while self.current_token and self.current_token.type.name == 'COMMA':
                self.advance()
                args.append(self.parse_expression())
        self.expect('RPAREN')
        return FunctionCallNode(VariableNode(func_token), args)

class Interpreter:
    """Interprets an AST for a strongly-typed language with Python-like imports."""
    def __init__(self):
        self.variables: Dict[str, Any] = {}  # Global variable scope
        self.functions: Dict[str, FunctionDefNode] = {}  # Function definitions
        self.classes: Dict[str, ClassNode] = {}  # Class definitions
        self.interfaces: Dict[str, InterfaceNode] = {}  # Interface definitions
        self.enums: Dict[str, EnumNode] = {}  # Enum definitions
        self.call_stack: List[Dict[str, Any]] = [self.variables]  # Scope stack
        self.imports: Dict[str, Any] = {}  # Imported modules (mock for now)

    def push_scope(self):
        """Pushes a new scope onto the call stack."""
        self.call_stack.append({})
        self.variables = self.call_stack[-1]

    def pop_scope(self):
        """Pops the current scope from the call stack."""
        self.call_stack.pop()
        self.variables = self.call_stack[-1] if self.call_stack else {}

    def interpret(self, node: ExpressionNode) -> Any:
        """Interprets an AST node and returns its evaluated result."""
        if isinstance(node, ProgramNode):
            for imp in node.imports:
                self.interpret_import(imp)
            for stmt in node.statements:
                result = self.interpret(stmt)
                if isinstance(result, ReturnNode):
                    return self.interpret_return(result)
            return None
        elif isinstance(node, ImportNode):
            return self.interpret_import(node)
        elif isinstance(node, NumberNode):
            return float(node.number.value) if '.' in node.number.value or 'e' in node.number.value.lower() else int(node.number.value)
        elif isinstance(node, StringNode):
            return node.string.value[1:-1]
        elif isinstance(node, CharNode):
            return node.char.value[1:-1]
        elif isinstance(node, BooleanNode):
            return node.boolean.value == 'true'
        elif isinstance(node, NullNode):
            return None
        elif isinstance(node, VariableNode):
            return self.get_variable(node.variable.value)
        elif isinstance(node, AssignNode):
            return self.interpret_assign(node)
        elif isinstance(node, VarDeclarationNode):
            return self.interpret_var_declaration(node)
        elif isinstance(node, ValDeclarationNode):
            return self.interpret_val_declaration(node)
        elif isinstance(node, ConstDeclarationNode):
            return self.interpret_const_declaration(node)
        elif isinstance(node, BinaryOperationNode):
            return self.interpret_binary_op(node)
        elif isinstance(node, UnaryOperationNode):
            return self.interpret_unary_op(node)
        elif isinstance(node, NullCoalesceNode):
            return self.interpret_null_coalesce(node)
        elif isinstance(node, ElvisNode):
            return self.interpret_elvis(node)
        elif isinstance(node, IfNode):
            return self.interpret_if(node)
        elif isinstance(node, WhileNode):
            return self.interpret_while(node)
        elif isinstance(node, DoWhileNode):
            return self.interpret_do_while(node)
        elif isinstance(node, ForNode):
            return self.interpret_for(node)
        elif isinstance(node, SwitchNode):
            return self.interpret_switch(node)
        elif isinstance(node, TryNode):
            return self.interpret_try(node)
        elif isinstance(node, ThrowNode):
            return self.interpret_throw(node)
        elif isinstance(node, FunctionDefNode):
            return self.interpret_function_def(node)
        elif isinstance(node, FunctionCallNode):
            return self.interpret_function_call(node)
        elif isinstance(node, LambdaNode):
            return self.interpret_lambda(node)
        elif isinstance(node, ClassNode):
            return self.interpret_class_def(node)
        elif isinstance(node, InterfaceNode):
            return self.interpret_interface_def(node)
        elif isinstance(node, EnumNode):
            return self.interpret_enum_def(node)
        elif isinstance(node, ReturnNode):
            return self.interpret_return(node)
        elif isinstance(node, PrintNode):
            return self.interpret_print(node)
        elif isinstance(node, InstanceOfNode):
            return self.interpret_instanceof(node)
        elif isinstance(node, NewNode):
            return self.interpret_new(node)
        elif isinstance(node, BlockNode):
            return self.interpret_block(node)
        elif isinstance(node, BreakNode):
            return node
        elif isinstance(node, ContinueNode):
            return node
        raise RuntimeError(f"Unknown node type: {type(node)}")

    def get_variable(self, name: str) -> Any:
        """Retrieves a variable's value from the current or parent scopes."""
        for scope in reversed(self.call_stack):
            if name in scope:
                return scope[name]
        raise RuntimeError(f"Undefined variable: {name}")

    def interpret_import(self, node: ImportNode) -> None:
        """Interprets a Python-style import (mock implementation).

        Example:
            import math;  // Stores 'math' in imports
            from os import path as ospath; // Stores 'ospath' -> 'os.path'
        """
        module_name = '.'.join(t.value for t in node.module)
        if node.names:
            for name in node.names:
                self.imports[name.value] = f"{module_name}.{name.value}"
        elif node.alias:
            self.imports[node.alias.value] = module_name
        else:
            self.imports[module_name] = module_name
        return None

    def interpret_assign(self, node: AssignNode) -> Any:
        """Interprets an assignment expression."""
        value = self.interpret(node.expression)
        for scope in reversed(self.call_stack):
            if node.variable.variable.value in scope:
                scope[node.variable.variable.value] = value
                return value
        self.variables[node.variable.variable.value] = value
        return value

    def interpret_var_declaration(self, node: VarDeclarationNode) -> Any:
        """Interprets a var declaration with optional type and initializer."""
        value = self.interpret(node.expr) if node.expr else None
        if node.type_token:
            self.check_type(value, node.type_token)
        self.variables[node.variable.variable.value] = value
        return value

    def interpret_val_declaration(self, node: ValDeclarationNode) -> Any:
        """Interprets a val (immutable) declaration."""
        value = self.interpret(node.expr)
        if node.type_token:
            self.check_type(value, node.type_token)
        self.variables[node.variable.variable.value] = value
        return value

    def interpret_const_declaration(self, node: ConstDeclarationNode) -> Any:
        """Interprets a const declaration."""
        value = self.interpret(node.expr)
        if node.type_token:
            self.check_type(value, node.type_token)
        self.variables[node.variable.variable.value] = value
        return value

    def check_type(self, value: Any, type_token: Token) -> None:
        """Checks if a value matches the expected type (basic type checking)."""
        type_name = type_token.type.name
        if type_name == 'INT' and not isinstance(value, int):
            raise RuntimeError(f"Expected int, got {type(value)}")
        elif type_name == 'FLOAT' and not isinstance(value, float):
            raise RuntimeError(f"Expected float, got {type(value)}")
        elif type_name == 'DOUBLE' and not isinstance(value, float):
            raise RuntimeError(f"Expected double, got {type(value)}")
        elif type_name == 'BOOLEAN' and not isinstance(value, bool):
            raise RuntimeError(f"Expected boolean, got {type(value)}")
        elif type_name == 'STRING_TYPE' and not isinstance(value, str):
            raise RuntimeError(f"Expected string, got {type(value)}")
        elif type_name == 'ANY':
            pass  # Any type allows all values
        elif type_name == 'VARIABLE' and not isinstance(value, dict):  # Class instance check
            raise RuntimeError(f"Expected instance of {type_token.value}, got {type(value)}")

    def interpret_binary_op(self, node: BinaryOperationNode) -> Any:
        """Interprets a binary operation."""
        left = self.interpret(node.left_node)
        right = self.interpret(node.right_node)
        op = node.operator.type.name
        try:
            if op == 'PLUS':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif op == 'MINUS':
                return left - right
            elif op == 'MULTIPLY':
                return left * right
            elif op == 'DIVIDE':
                if right == 0:
                    raise RuntimeError("Division by zero")
                return left / right
            elif op == 'MODULO':
                return left % right
            elif op == 'EQUAL':
                return left == right
            elif op == 'NOT_EQUAL':
                return left != right
            elif op == 'LESS':
                return left < right
            elif op == 'GREATER':
                return left > right
            elif op == 'LESS_EQUAL':
                return left <= right
            elif op == 'GREATER_EQUAL':
                return left >= right
            elif op == 'AND':
                return left and right
            elif op == 'OR':
                return left or right
            elif op == 'BIT_AND':
                return left & right
            elif op == 'BIT_OR':
                return left | right
            elif op == 'BIT_XOR':
                return left ^ right
            elif op == 'SHL':
                return left << right
            elif op == 'SHR':
                return left >> right
            raise RuntimeError(f"Unknown operator: {op}")
        except TypeError as e:
            raise RuntimeError(f"Type error in operation {op}: {e}")

    def interpret_unary_op(self, node: UnaryOperationNode) -> Any:
        """Interprets a unary operation."""
        operand = self.interpret(node.operand)
        op = node.operator.type.name
        try:
            if op == 'MINUS':
                return -operand
            elif op == 'NOT':
                return not operand
            elif op == 'BIT_NOT':
                return ~operand
            raise RuntimeError(f"Unknown unary operator: {op}")
        except TypeError as e:
            raise RuntimeError(f"Type error in unary operation {op}: {e}")

    def interpret_null_coalesce(self, node: NullCoalesceNode) -> Any:
        """Interprets a null-coalescing operation (??)."""
        left = self.interpret(node.left_node)
        return left if left is not None else self.interpret(node.right_node)

    def interpret_elvis(self, node: ElvisNode) -> Any:
        """Interprets an Elvis operation (?:)."""
        left = self.interpret(node.left_node)
        return left if left is not None else self.interpret(node.right_node)

    def interpret_if(self, node: IfNode) -> Any:
        """Interprets an if statement."""
        condition = self.interpret(node.condition)
        if not isinstance(condition, bool):
            raise RuntimeError(f"Condition must be boolean, got {type(condition)}")
        if condition:
            return self.interpret(node.then_branch)
        elif node.else_branch:
            return self.interpret(node.else_branch)
        return None

    def interpret_while(self, node: WhileNode) -> Any:
        """Interprets a while loop."""
        while True:
            condition = self.interpret(node.condition)
            if not isinstance(condition, bool):
                raise RuntimeError(f"Condition must be boolean, got {type(condition)}")
            if not condition:
                break
            result = self.interpret(node.body)
            if isinstance(result, BreakNode):
                break
            elif isinstance(result, ReturnNode):
                return result
            elif isinstance(result, ContinueNode):
                continue
        return None

    def interpret_do_while(self, node: DoWhileNode) -> Any:
        """Interprets a do-while loop."""
        while True:
            result = self.interpret(node.body)
            if isinstance(result, BreakNode):
                break
            elif isinstance(result, ReturnNode):
                return result
            elif isinstance(result, ContinueNode):
                continue
            condition = self.interpret(node.condition)
            if not isinstance(condition, bool):
                raise RuntimeError(f"Condition must be boolean, got {type(condition)}")
            if not condition:
                break
        return None

    def interpret_for(self, node: ForNode) -> Any:
        """Interprets a for loop."""
        if node.init:
            self.interpret(node.init)
        self.push_scope()
        try:
            while node.cond is None or self.interpret(node.cond):
                result = self.interpret(node.body)
                if isinstance(result, BreakNode):
                    break
                elif isinstance(result, ReturnNode):
                    return result
                elif isinstance(result, ContinueNode):
                    if node.step:
                        self.interpret(node.step)
                    continue
                if node.step:
                    self.interpret(node.step)
            return None
        finally:
            self.pop_scope()

    def interpret_switch(self, node: SwitchNode) -> Any:
        """Interprets a switch statement."""
        value = self.interpret(node.expression)
        for case in node.cases:
            case_value = self.interpret(case.value)
            if value == case_value:
                return self.interpret(case.body)
        if node.default:
            return self.interpret(node.default)
        return None

    def interpret_try(self, node: TryNode) -> Any:
        """Interprets a try-catch-finally block."""
        try:
            return self.interpret(node.try_block)
        except RuntimeError as e:
            for catch in node.catches:
                self.push_scope()
                try:
                    self.variables[catch.exception_var.variable.value] = str(e)
                    return self.interpret(catch.body)
                finally:
                    self.pop_scope()
            raise
        finally:
            if node.finally_block:
                self.interpret(node.finally_block)

    def interpret_throw(self, node: ThrowNode) -> None:
        """Interprets a throw statement."""
        value = self.interpret(node.expression)
        raise RuntimeError(str(value))

    def interpret_function_def(self, node: FunctionDefNode) -> None:
        """Interprets a function definition."""
        self.functions[node.name.value] = node
        return None

    def interpret_function_call(self, node: FunctionCallNode) -> Any:
        """Interprets a function call."""
        func_name = node.func.variable.value
        if func_name not in self.functions:
            raise RuntimeError(f"Undefined function: {func_name}")
        func = self.functions[func_name]
        args = [self.interpret(arg) for arg in node.args]
        if len(args) != len(func.params):
            raise RuntimeError(f"Expected {len(func.params)} arguments, got {len(args)}")
        self.push_scope()
        try:
            for param, arg in zip(func.params, args):
                if param.type_token:
                    self.check_type(arg, param.type_token)
                if arg is None and not param.is_nullable:
                    raise RuntimeError(f"Parameter {param.name.value} is not nullable")
                self.variables[param.name.value] = arg
            result = self.interpret(func.body)
            if isinstance(result, ReturnNode):
                return self.interpret_return(result)
            return None
        finally:
            self.pop_scope()

    def interpret_lambda(self, node: LambdaNode) -> Any:
        """Interprets a lambda expression (returns a callable)."""
        def lambda_func(*args):
            if len(args) != len(node.params):
                raise RuntimeError(f"Expected {len(node.params)} arguments, got {len(args)}")
            self.push_scope()
            try:
                for param, arg in zip(node.params, args):
                    if param.type_token:
                        self.check_type(arg, param.type_token)
                    if arg is None and not param.is_nullable:
                        raise RuntimeError(f"Parameter {param.name.value} is not nullable")
                    self.variables[param.name.value] = arg
                return self.interpret(node.body)
            finally:
                self.pop_scope()
        return lambda_func

    def interpret_class_def(self, node: ClassNode) -> None:
        """Interprets a class definition."""
        self.classes[node.name.value] = node
        return None

    def interpret_interface_def(self, node: InterfaceNode) -> None:
        """Interprets an interface definition."""
        self.interfaces[node.name.value] = node
        return None

    def interpret_enum_def(self, node: EnumNode) -> None:
        """Interprets an enum definition."""
        self.enums[node.name.value] = node
        for value in node.values:
            self.variables[value.value] = value.value
        return None

    def interpret_return(self, node: ReturnNode) -> Any:
        """Interprets a return statement."""
        return self.interpret(node.expression) if node.expression else None

    def interpret_print(self, node: PrintNode) -> None:
        """Interprets a print statement."""
        value = self.interpret(node.expression)
        print(value)
        return None

    def interpret_instanceof(self, node: InstanceOfNode) -> bool:
        """Interprets an instanceof expression."""
        value = self.interpret(node.expression)
        type_name = node.type_token.value
        if node.type_token.type.name == 'VARIABLE':
            return isinstance(value, dict) and value.get('__class__') == type_name
        elif node.type_token.type.name == 'INT':
            return isinstance(value, int)
        elif node.type_token.type.name in ('FLOAT', 'DOUBLE'):
            return isinstance(value, float)
        elif node.type_token.type.name == 'BOOLEAN':
            return isinstance(value, bool)
        elif node.type_token.type.name == 'STRING_TYPE':
            return isinstance(value, str)
        elif node.type_token.type.name == 'ANY':
            return True
        return False

    def interpret_new(self, node: NewNode) -> Any:
        """Interprets object instantiation."""
        class_name = node.type_token.value
        if class_name not in self.classes:
            raise RuntimeError(f"Undefined class: {class_name}")
        args = [self.interpret(arg) for arg in node.args]
        instance = {'__class__': class_name}
        return instance

    def interpret_block(self, node: BlockNode) -> Any:
        """Interprets a block of statements."""
        self.push_scope()
        try:
            for stmt in node.statements:
                result = self.interpret(stmt)
                if isinstance(result, (ReturnNode, BreakNode, ContinueNode)):
                    return result
            return None
        finally:
            self.pop_scope()