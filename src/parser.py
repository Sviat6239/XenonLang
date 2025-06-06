from abc import ABC
from typing import List, Optional, Any, Dict
from .token import Token, TokenType, token_types_list
from .ast import *
from .error import format_error

class Parser:
    """Parses a list of tokens into an AST for a strongly-typed language with Python-like imports."""
    def __init__(self, tokens: List[Token], source: str, filename: str):
        self.tokens = tokens
        self.source = source
        self.filename = filename
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
        raise SyntaxError(format_error(
            "SyntaxError",
            f"Expected {token_type_name}, got {self.current_token.type.name if self.current_token else 'EOF'}",
            self.filename,
            self.source,
            self.current_token.line if self.current_token else 1,
            self.current_token.column if self.current_token else 1
        ))

    def expect_one_of(self, token_type_names: tuple) -> Token:
        """Expects one of the specified token types."""
        if self.current_token and self.current_token.type.name in token_type_names:
            token = self.current_token
            self.advance()
            return token
        raise SyntaxError(format_error(
            "SyntaxError",
            f"Expected one of {token_type_names}, got {self.current_token.type.name if self.current_token else 'EOF'}",
            self.filename,
            self.source,
            self.current_token.line if self.current_token else 1,
            self.current_token.column if self.current_token else 1
        ))

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
        while self.current_token and self.current_token.type.name != 'EOF':
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
            raise SyntaxError(format_error(
                "SyntaxError",
                "Unexpected end of input",
                self.filename,
                self.source,
                1, 1
            ))
        
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
            type_token = self.current_token
            if type_token.type.name in ('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'VOID', 'ANY'):
                self.advance()
            elif type_token.type.name == 'VARIABLE' and type_token.value == 'str':
                type_token = Token(TokenType('STRING_TYPE', r'\bstring\b'), 'string', type_token.position, type_token.line, type_token.column)
                self.advance()
            else:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    f"Expected type, got {type_token.type.name}",
                    self.filename,
                    self.source,
                    type_token.line,
                    type_token.column
                ))
            if self.current_token and self.current_token.type.name == 'NULLABLE':
                self.advance()  # Consume '?' for nullable types
        expr = None
        if self.current_token and self.current_token.type.name == 'ASSIGN':
            self.advance()
            expr = self.parse_expression()
        self.expect('SEMICOLON')
        if decl_type == 'VAR':
            return VarDeclarationNode(expr)
        elif decl_type == 'VAL':
            if not expr:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    "Val declaration requires an initializer",
                    self.filename,
                    self.source,
                    decl_token.line,
                    decl_token.column
                ))
            return ValDeclarationNode(decl_token)
        else:  # CONST
            if not expr:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    "Const declaration requires an initializer",
                    self.filename,
                    self.source,
                    decl_token.line,
                    decl_token.column
                ))
            return ConstDeclarationNode(expr.value)

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
                type_token = self.current_token
                if type_token.type.name in ('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'ANY'):
                    self.advance()
                elif type_token.type.name == 'VARIABLE' and type_token.value == 'str':
                    type_token = Token(TokenType('STRING_TYPE', r'\bstring\b'), 'string', type_token.position, type_token.line, type_token.column)
                    self.advance()
                else:
                    raise SyntaxError(format_error(
                        "SyntaxError",
                        f"Expected type, got {type_token.type.name}",
                        self.filename,
                        self.source,
                        type_token.line,
                        type_token.column
                    ))
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
            return_type = self.current_token
            if return_type.type.name in ('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'VOID', 'ANY'):
                self.advance()
            elif return_type.type.name == 'VARIABLE' and return_type.value == 'str':
                return_type = Token(TokenType('STRING_TYPE', r'\bstring\b'), 'string', return_type.position, return_type.line, return_type.column)
                self.advance()
            else:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    f"Expected type, got {return_type.type.name}",
                    self.filename,
                    self.source,
                    return_type.line,
                    return_type.column
                ))
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
            type_token = self.current_token
            if type_token.type.name in ('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'ANY'):
                self.advance()
            elif type_token.type.name == 'VARIABLE' and type_token.value == 'str':
                type_token = Token(TokenType('STRING_TYPE', r'\bstring\b'), 'string', type_token.position, type_token.line, type_token.column)
                self.advance()
            else:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    f"Expected type, got {type_token.type.name}",
                    self.filename,
                    self.source,
                    type_token.line,
                    type_token.column
                ))
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
            token = self.current_token
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
            token = self.current_token
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
                raise SyntaxError(format_error(
                    "SyntaxError",
                    "Invalid assignment target",
                    self.filename,
                    self.source,
                    token.line,
                    token.column
                ))
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
            raise SyntaxError(format_error(
                "SyntaxError",
                "Expected expression, got EOF",
                self.filename,
                self.source,
                1, 1
            ))
        
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
                'print', 'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'default', 'return', 'fun',
                'class', 'interface', 'enum', 'var', 'val', 'const', 'break', 'continue',
                'try', 'catch', 'finally', 'throw', 'true', 'false', 'null', 'public',
                'private', 'protected', 'internal', 'static', 'new', 'this', 'super',
                'instanceof', 'lambda', 'import', 'from', 'as', 'elvis'
            }
            if token.value.lower() in keyword_values:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    f"Unexpected keyword '{token.value}' used as variable",
                    self.filename,
                    self.source,
                    token.line,
                    token.column
                ))
            if self.current_token and self.current_token.type.name == 'LPAREN':
                return self.parse_function_call(token)
            return VariableNode(token)
        elif token.type.name == 'LPAREN':
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        raise SyntaxError(format_error(
            "SyntaxError",
            f"Unexpected token {token.type.name}",
            self.filename,
            self.source,
            token.line,
            token.column
        ))

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