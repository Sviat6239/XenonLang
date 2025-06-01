from .token import tokenTypesList
from .token import Token
from .ast import *


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.scope = {}

    def match(self, *expected):
        if self.pos < len(self.tokens):
            current_token = self.tokens[self.pos]
            if any(t.name == current_token.type.name for t in expected):
                self.pos += 1
                return current_token
        return None

    def require(self, *expected):
        token = self.match(*expected)
        if not token:
            raise Exception(f"на позиции {self.pos} ожидается {expected[0].name}")
        return token

    def parse_primary(self):
        if self.match(tokenTypesList['LPAR']):
            expr = self.parse_expression()
            self.require(tokenTypesList['RPAR'])
            return expr
        if number := self.match(tokenTypesList['NUMBER']):
            return NumberNode(number)
        if string := self.match(tokenTypesList['STRING']):
            return StringNode(string)
        if boolean := self.match(tokenTypesList['BOOLEAN']):
            return BooleanNode(boolean)
        if null := self.match(tokenTypesList['NULL']):
            return NullNode(null)
        if ident := self.match(tokenTypesList['VARIABLE']):
            if self.match(tokenTypesList['LPAR']):
                args = []
                if not self.match(tokenTypesList['RPAR']):
                    args.append(self.parse_expression())
                    while self.match(tokenTypesList['COMMA']):
                        args.append(self.parse_expression())
                    self.require(tokenTypesList['RPAR'])
                return FunctionCallNode(VariableNode(ident), args)
            return VariableNode(ident)
        raise Exception(f"Unexpected token at position {self.pos}")

    def parse_unary(self):
        if op := self.match(tokenTypesList['MINUS'], tokenTypesList['LOG']):
            return UnaryOperationNode(op, self.parse_unary())
        return self.parse_primary()

    def parse_term(self):
        node = self.parse_unary()
        while op := self.match(tokenTypesList['MUL'], tokenTypesList['DIV']):
            node = BinOperationNode(op, node, self.parse_unary())
        return node

    def parse_formula(self):
        node = self.parse_term()
        while op := self.match(tokenTypesList['PLUS'], tokenTypesList['MINUS']):
            node = BinOperationNode(op, node, self.parse_term())
        return node

    def parse_assignment(self):
        node = self.parse_formula()
        if isinstance(node, VariableNode) and (op := self.match(tokenTypesList['ASSIGN'])):
            return AssignNode(op, node, self.parse_assignment())
        return node

    def parse_expression(self):
        return self.parse_assignment()

    def parse_print(self):
        if op := self.match(tokenTypesList['LOG']):
            expr = self.parse_expression()
            return PrintNode(expr)
        return None

    def parse_return(self):
        if self.match(tokenTypesList['RETURN']):
            if self.match(tokenTypesList['SEMICOLON']):
                return ReturnNode(None)
            expr = self.parse_expression()
            self.require(tokenTypesList['SEMICOLON'])
            return ReturnNode(expr)
        return None

    def parse_if(self):
        if self.match(tokenTypesList['IF']):
            self.require(tokenTypesList['LPAR'])
            condition = self.parse_expression()
            self.require(tokenTypesList['RPAR'])
            then_branch = self.parse_code_block()
            else_branch = None
            if self.match(tokenTypesList['ELSE']):
                else_branch = self.parse_code_block()
            return IfNode(condition, then_branch, else_branch)
        return None

    def parse_while(self):
        if self.match(tokenTypesList['WHILE']):
            self.require(tokenTypesList['LPAR'])
            condition = self.parse_expression()
            self.require(tokenTypesList['RPAR'])
            body = self.parse_code_block()
            return WhileNode(condition, body)
        return None

    def parse_for(self):
        if self.match(tokenTypesList['FOR']):
            self.require(tokenTypesList['LPAR'])
            init = self.parse_expression()
            self.require(tokenTypesList['SEMICOLON'])
            cond = self.parse_expression()
            self.require(tokenTypesList['SEMICOLON'])
            step = self.parse_expression()
            self.require(tokenTypesList['RPAR'])
            body = self.parse_code_block()
            return ForNode(init, cond, step, body)
        return None

    def parse_function(self):
        if self.match(tokenTypesList['FUNCTION']):
            name = self.require(tokenTypesList['VARIABLE'])
            self.require(tokenTypesList['LPAR'])
            params = []
            if not self.match(tokenTypesList['RPAR']):
                params.append(self.require(tokenTypesList['VARIABLE']))
                while self.match(tokenTypesList['COMMA']):
                    params.append(self.require(tokenTypesList['VARIABLE']))
                self.require(tokenTypesList['RPAR'])
            body = self.parse_code_block()
            return FunctionDefNode(name, params, body)
        return None

    def parse_statement(self):
        return (
            self.parse_if() or
            self.parse_while() or
            self.parse_for() or
            self.parse_function() or
            self.parse_return() or
            self.parse_print() or
            self.parse_expression()
        )

    def parse_code_block(self):
        block = StatementsNode()
        self.require(tokenTypesList['LBRACE'])
        while not self.match(tokenTypesList['RBRACE']):
            stmt = self.parse_statement()
            if not isinstance(stmt, ReturnNode):
                self.require(tokenTypesList['SEMICOLON'])
            block.add_node(stmt)
        return block

    def parse_code(self):
        root = StatementsNode()
        while self.pos < len(self.tokens):
            stmt = self.parse_statement()
            if not isinstance(stmt, ReturnNode):
                self.require(tokenTypesList['SEMICOLON'])
            root.add_node(stmt)
        return root
