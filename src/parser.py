from abc import ABC
from typing import List, Optional, Callable
from .token import Token, TokenType, token_types_list, token_types
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
        if not self.current_token:
            raise SyntaxError(format_error(
                "SyntaxError",
                f"Expected {token_type_name}, got EOF",
                self.filename,
                self.source,
                self.tokens[-1].line if self.tokens else 1,
                self.tokens[-1].column if self.tokens else 1
            ))
        if self.current_token.type.name == token_type_name:
            token = self.current_token
            self.advance()
            return token
        raise SyntaxError(format_error(
            "SyntaxError",
            f"Expected {token_type_name}, got {self.current_token.type.name}",
            self.filename,
            self.source,
            self.current_token.line,
            self.current_token.column
        ))

    def expect_one_of(self, token_type_names: tuple) -> Token:
        """Expects one of the specified token types."""
        if not self.current_token:
            raise SyntaxError(format_error(
                "SyntaxError",
                f"Expected one of {token_type_names}, got EOF",
                self.filename,
                self.source,
                self.tokens[-1].line if self.tokens else 1,
                self.tokens[-1].column if self.tokens else 1
            ))
        if self.current_token.type.name in token_type_names:
            token = self.current_token
            self.advance()
            return token
        raise SyntaxError(format_error(
            "SyntaxError",
            f"Expected one of {token_type_names}, got {self.current_token.type.name}",
            self.filename,
            self.source,
            self.current_token.line,
            self.current_token.column
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
        if not self.current_token:
            raise SyntaxError(format_error(
                "SyntaxError",
                "Unexpected end of file, expecting EOF",
                self.filename,
                self.source,
                self.tokens[-1].line if self.tokens else 1,
                self.tokens[-1].column if self.tokens else 1
            ))
        self.expect('EOF')
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
                self.tokens[-1].line if self.tokens else 1,
                self.tokens[-1].column if self.tokens else 1
            ))
        
        if self.current_token.type.name in ('VAR', 'VAL', 'CONST'):
            return self.parse_declaration()
        elif self.current_token.type.name in ('PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL', 'STATIC'):
            modifiers = []
            while self.current_token and self.current_token.type.name in ('PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL', 'STATIC'):
                modifiers.append(self.current_token)
                self.advance()
            if self.current_token.type.name == 'FUNCTION':
                return self.parse_function_def(modifiers)
            elif self.current_token.type.name in ('VAR', 'VAL', 'CONST'):
                return self.parse_declaration(modifiers)
            elif self.current_token.type.name == 'CLASS':
                return self.parse_class_def(modifiers)
            elif self.current_token.type.name == 'INTERFACE':
                return self.parse_interface_def(modifiers)
            else:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    f"Expected declaration after modifiers, got {self.current_token.type.name}",
                    self.filename,
                    self.source,
                    self.current_token.line,
                    self.current_token.column
                ))
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

    def parse_declaration(self, modifiers: List[Token] = None) -> ExpressionNode:
        """Parses variable declarations (var, val, const) with optional type annotations and modifiers.

        Example:
            public var x: int = 5;     // VarDeclarationNode(var_token, VariableNode('x'), Token('INT'), NumberNode('5'), modifiers=['public'])
        """
        if not modifiers:
            modifiers = []
        decl_type = self.current_token.type.name
        decl_token = self.expect(decl_type)
        variable = VariableNode(self.expect('VARIABLE'))
        type_token = None
        if self.current_token and self.current_token.type.name == 'COLON':
            self.advance()
            type_token = self.parse_type()
        expr = None
        if self.current_token and self.current_token.type.name == 'ASSIGN':
            self.advance()
            expr = self.parse_expression()
        self.expect('SEMICOLON')
        if decl_type == 'VAR':
            return VarDeclarationNode(decl_token, variable, type_token, expr, modifiers)
        elif decl_type == 'VAL':
            if not expr and 'CONST' not in [mod.value for mod in modifiers]:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    "Val declaration requires an initializer unless const",
                    self.filename,
                    self.source,
                    decl_token.line,
                    decl_token.column
                ))
            return ValDeclarationNode(decl_token, variable, type_token, expr, modifiers)
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
            return ConstDeclarationNode(decl_token, variable, type_token, expr, modifiers)

    def parse_type(self) -> Callable[[bool], Token]:
        """Parses a type annotation (e.g., 'int', 'string', 'int?')."""
        if not self.current_token:
            raise SyntaxError(format_error(
                "SyntaxError",
                "Expected type, got EOF",
                self.filename,
                self.source,
                self.tokens[-1].line if self.tokens else 1,
                self.tokens[-1].column if self.tokens else 1
            ))
        type_token = self.current_token
        if type_token.type.name in ('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'VOID', 'ANY'):
            self.advance()
            is_nullable = self.current_token and self.current_token.type.name == 'NULLABLE'
            if is_nullable:
                self.advance()
            return lambda nullable: Token(type_token.type, type_token.value, type_token.position, type_token.line, type_token.column, nullable)
        elif type_token.type.name == 'VARIABLE' and type_token.value == 'str':
            type_token = Token(token_types['STRING_TYPE'], 'string', type_token.position, type_token.line, type_token.column)
            self.advance()
            is_nullable = self.current_token and self.current_token.type.name == 'NULLABLE'
            if is_nullable:
                self.advance()
            return lambda nullable: Token(type_token.type, type_token.value, type_token.position, type_token.line, type_token.column, nullable)
        elif type_token.type.name == 'VARIABLE':
            self.advance()
            is_nullable = self.current_token and self.current_token.type.name == 'NULLABLE'
            if is_nullable:
                self.advance()
            return lambda nullable: Token(type_token.type, type_token.value, type_token.position, type_token.line, type_token.column, nullable)
        raise SyntaxError(format_error(
            "SyntaxError",
            f"Expected type, got {type_token.type.name}",
            self.filename,
            self.source,
            type_token.line,
            type_token.column
        ))

    def parse_if_statement(self) -> IfNode:
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
        self.expect('WHILE')
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_do_while_statement(self) -> DoWhileNode:
        self.expect('DO')
        body = self.parse_block()
        self.expect('WHILE')
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        return DoWhileNode(body, condition)

    def parse_for_statement(self) -> ForNode:
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
            else:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    f"Expected 'case' or 'default', got {self.current_token.type.name}",
                    self.filename,
                    self.source,
                    self.current_token.line,
                    self.current_token.column
                ))
        self.expect('RBRACE')
        return SwitchNode(expression, cases, default)

    def parse_try_statement(self) -> TryNode:
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
                type_token = self.parse_type()
            self.expect('RPAREN')
            body = self.parse_block()
            catches.append(CatchNode(exception_var, type_token, body))
        finally_block = None
        if self.current_token and self.current_token.type.name == 'FINALLY':
            self.advance()
            finally_block = self.parse_block()
        return TryNode(try_block, catches, finally_block)

    def parse_throw_statement(self) -> ThrowNode:
        self.expect('THROW')
        expr = self.parse_expression()
        self.expect('SEMICOLON')
        return ThrowNode(expr)

    def parse_function_def(self, modifiers: List[Token] = None) -> FunctionDefNode:
        if not modifiers:
            modifiers = []
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
            return_type = self.parse_type()
        body = self.parse_block()
        return FunctionDefNode(name, params, return_type, body, modifiers)

    def parse_param(self) -> ParamNode:
        name = self.expect('VARIABLE')
        type_token = None
        is_nullable = False
        if self.current_token and self.current_token.type.name == 'COLON':
            self.advance()
            type_token = self.parse_type()
            is_nullable = type_token.is_nullable
        return ParamNode(name, type_token, is_nullable)

    def parse_class_def(self, modifiers: List[Token] = None) -> ClassNode:
        if not modifiers:
            modifiers = []
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
            if self.current_token.type.name in ('PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL', 'STATIC'):
                member_modifiers = []
                while self.current_token and self.current_token.type.name in ('PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL', 'STATIC'):
                    member_modifiers.append(self.current_token)
                    self.advance()
                if self.current_token.type.name in ('VAR', 'VAL', 'CONST'):
                    members.append(self.parse_declaration(member_modifiers))
                elif self.current_token.type.name == 'FUNCTION':
                    members.append(self.parse_function_def(member_modifiers))
                else:
                    raise SyntaxError(format_error(
                        "SyntaxError",
                        f"Expected member declaration, got {self.current_token.type.name}",
                        self.filename,
                        self.source,
                        self.current_token.line,
                        self.current_token.column
                    ))
            elif self.current_token.type.name in ('VAR', 'VAL', 'CONST', 'FUNCTION'):
                members.append(self.parse_statement())
            else:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    f"Expected member declaration, got {self.current_token.type.name}",
                    self.filename,
                    self.source,
                    self.current_token.line,
                    self.current_token.column
                ))
        self.expect('RBRACE')
        return ClassNode(name, superclass, interfaces, members, modifiers)

    def parse_interface_def(self, modifiers: List[Token] = None) -> InterfaceNode:
        if not modifiers:
            modifiers = []
        self.expect('INTERFACE')
        name = self.expect('VARIABLE')
        self.expect('LBRACE')
        members = []
        while self.current_token and self.current_token.type.name != 'RBRACE':
            if self.current_token.type.name in ('PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL', 'STATIC'):
                member_modifiers = []
                while self.current_token and self.current_token.type.name in ('PUBLIC', 'PRIVATE', 'PROTECTED', 'INTERNAL', 'STATIC'):
                    member_modifiers.append(self.current_token)
                    self.advance()
                if self.current_token.type.name == 'FUNCTION':
                    members.append(self.parse_function_def(member_modifiers))
                else:
                    raise SyntaxError(format_error(
                        "SyntaxError",
                        f"Expected function declaration in interface, got {self.current_token.type.name}",
                        self.filename,
                        self.source,
                        self.current_token.line,
                        self.current_token.column
                    ))
            elif self.current_token.type.name == 'FUNCTION':
                members.append(self.parse_function_def())
            else:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    f"Expected function declaration in interface, got {self.current_token.type.name}",
                    self.filename,
                    self.source,
                    self.current_token.line,
                    self.current_token.column
                ))
        self.expect('RBRACE')
        return InterfaceNode(name, members, modifiers)

    def parse_enum_def(self) -> EnumNode:
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
                elif self.current_token and self.current_token.type.name != 'RBRACE':
                    raise SyntaxError(format_error(
                        "SyntaxError",
                        "Expected comma or '}' after enum value",
                        self.filename,
                        self.source,
                        self.current_token.line,
                        self.current_token.column
                    ))
            else:
                members.append(self.parse_statement())
        self.expect('RBRACE')
        return EnumNode(name, values, members)

    def parse_return_statement(self) -> ReturnNode:
        self.expect('RETURN')
        expr = self.parse_expression() if self.current_token and self.current_token.type.name != 'SEMICOLON' else None
        self.expect('SEMICOLON')
        return ReturnNode(expr)

    def parse_print_statement(self) -> PrintNode:
        self.expect('PRINT')
        self.expect('LPAREN')
        expr = self.parse_expression()
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        return PrintNode(expr)

    def parse_block(self) -> BlockNode:
        self.expect('LBRACE')
        statements = []
        while self.current_token and self.current_token.type.name != 'RBRACE':
            if not self.current_token:
                raise SyntaxError(format_error(
                    "SyntaxError",
                    "Unclosed block, expected '}'",
                    self.filename,
                    self.source,
                    self.tokens[-1].line if self.tokens else 1,
                    self.tokens[-1].column if self.tokens else 1
                ))
            statements.append(self.parse_statement())
        self.expect('RBRACE')
        return BlockNode(statements)

    def parse_expression(self) -> ExpressionNode:
        return self.parse_null_coalesce()

    def parse_null_coalesce(self) -> ExpressionNode:
        expr = self.parse_elvis()
        while self.current_token and self.current_token.type.name == 'NULL_COALESCE':
            token = self.current_token
            self.advance()
            right = self.parse_elvis()
            expr = NullCoalesceNode(expr, right)
        return expr

    def parse_elvis(self) -> ExpressionNode:
        expr = self.parse_assignment()
        while self.current_token and self.current_token.type.name == 'ELVIS':
            token = self.current_token
            self.advance()
            right = self.parse_assignment()
            expr = ElvisNode(expr, right)
        return expr

    def parse_assignment(self) -> ExpressionNode:
        expr = self.parse_equality()
        if self.current_token and self.current_token.type.name == 'ASSIGN':
            token = self.current_token
            self.advance()
            if not isinstance(expr, (VariableNode, MemberCallNode)):
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
        expr = self.parse_comparison()
        while self.current_token and self.current_token.type.name in ('EQUAL', 'NOT_EQUAL'):
            token = self.current_token
            self.advance()
            right = self.parse_comparison()
            expr = BinaryOperationNode(token, expr, right)
        return expr

    def parse_comparison(self) -> ExpressionNode:
        expr = self.parse_term()
        while self.current_token and self.current_token.type.name in ('LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL'):
            token = self.current_token
            self.advance()
            right = self.parse_term()
            expr = BinaryOperationNode(token, expr, right)
        return expr

    def parse_term(self) -> ExpressionNode:
        expr = self.parse_factor()
        while self.current_token and self.current_token.type.name in ('PLUS', 'MINUS'):
            token = self.current_token
            self.advance()
            right = self.parse_factor()
            expr = BinaryOperationNode(token, expr, right)
        return expr

    def parse_factor(self) -> ExpressionNode:
        expr = self.parse_unary()
        while self.current_token and self.current_token.type.name in ('MULTIPLY', 'DIVIDE', 'MODULO'):
            token = self.current_token
            self.advance()
            right = self.parse_unary()
            expr = BinaryOperationNode(token, expr, right)
        return expr

    def parse_unary(self) -> ExpressionNode:
        if self.current_token and self.current_token.type.name in ('MINUS', 'NOT', 'BIT_NOT'):
            token = self.current_token
            self.advance()
            operand = self.parse_unary()
            return UnaryOperationNode(token, operand)
        return self.parse_postfix()

    def parse_postfix(self) -> ExpressionNode:
        """Parses postfix operations like increment/decrement and member access."""
        expr = self.parse_instanceof()
        while self.current_token and self.current_token.type.name in ('INCREMENT', 'DECREMENT', 'DOT'):
            if self.current_token.type.name in ('INCREMENT', 'DECREMENT'):
                token = self.current_token
                self.advance()
                expr = UnaryOperationNode(token, expr, is_postfix=True)
            elif self.current_token.type.name == 'DOT':
                self.advance()
                method = VariableNode(self.expect('VARIABLE'))
                if self.current_token and self.current_token.type.name == 'LPAREN':
                    self.expect('LPAREN')
                    args = []
                    if self.current_token and self.current_token.type.name != 'RPAREN':
                        args.append(self.parse_expression())
                        while self.current_token and self.current_token.type.name == 'COMMA':
                            self.advance()
                            args.append(self.parse_expression())
                    self.expect('RPAREN')
                    expr = MemberCallNode(expr, method, args)
                else:
                    raise SyntaxError(format_error(
                        "SyntaxError",
                        "Member access without method call not supported",
                        self.filename,
                        self.source,
                        method.variable.line,
                        method.variable.column
                    ))
        return expr

    def parse_instanceof(self) -> ExpressionNode:
        expr = self.parse_new()
        if self.current_token and self.current_token.type.name == 'INSTANCEOF':
            self.advance()
            type_token = self.expect_one_of(('INT', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'STRING_TYPE', 'ANY', 'VARIABLE'))
            return InstanceOfNode(expr, type_token)
        return expr

    def parse_new(self) -> ExpressionNode:
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
        """Parses a primary expression (e.g., number, string, variable, 'this', 'super', parenthesized expression)."""
        if not self.current_token:
            raise SyntaxError(format_error(
                "SyntaxError",
                "Expected expression, got EOF",
                self.filename,
                self.source,
                self.tokens[-1].line if self.tokens else 1,
                self.tokens[-1].column if self.tokens else 1
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
        elif token.type.name == 'THIS':
            return ThisNode(token)
        elif token.type.name == 'SUPER':
            return SuperNode(token)
        elif token.type.name == 'VARIABLE':
            keyword_values = {
                'print', 'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'default', 'return', 'fun',
                'class', 'interface', 'enum', 'var', 'val', 'const', 'break', 'continue',
                'try', 'catch', 'finally', 'throw', 'true', 'false', 'null', 'public',
                'private', 'protected', 'internal', 'static', 'new', 'this', 'super',
                'instanceof', 'lambda', 'import', 'from', 'as'
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
        self.expect('LPAREN')
        args = []
        if self.current_token and self.current_token.type.name != 'RPAREN':
            args.append(self.parse_expression())
            while self.current_token and self.current_token.type.name == 'COMMA':
                self.advance()
                args.append(self.parse_expression())
        self.expect('RPAREN')
        return FunctionCallNode(VariableNode(func_token), args)