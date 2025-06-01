from .token import token_types_list, Token
from .ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.scope = {
            'print': lambda args: print(*args)
        }

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def match(self, *expected):
        while True:
            current = self.peek()
            if not current or current.type.name not in ('SPACE', 'COMMENT'):
                break
            self.advance()
        current = self.peek()
        if current and any(current.type.name == t.name for t in expected):
            self.advance()
            return current
        return None

    def require(self, *expected):
        token = self.match(*expected)
        if not token:
            expected_names = ', '.join(t.name for t in expected)
            current = self.peek()
            pos = current.position if current else 'EOF'
            found = current.type.name if current else 'EOF'
            raise Exception(f"Expected one of the tokens [{expected_names}], but found {found} at position {pos}")
        return token

    def parse_primary(self):
        if self.match(token_types_list['LPAREN']):
            expr = self.parse_expression()
            self.require(token_types_list['RPAREN'])
            return expr

        if number := self.match(token_types_list['NUMBER']):
            return NumberNode(number)

        if string := self.match(token_types_list['STRING']):
            return StringNode(string)

        if boolean := self.match(token_types_list['TRUE'], token_types_list['FALSE']):
            return BooleanNode(boolean)

        if null := self.match(token_types_list['NULL']):
            return NullNode(null)

        if ident := self.match(token_types_list['VARIABLE']):
            if self.match(token_types_list['LPAREN']):
                if self.match(token_types_list['RPAREN']):
                    return FunctionCallNode(VariableNode(ident), [])
                args = [self.parse_expression()]
                while self.match(token_types_list['COMMA']):
                    args.append(self.parse_expression())
                self.require(token_types_list['RPAREN'])
                return FunctionCallNode(VariableNode(ident), args)
            return VariableNode(ident)

        raise Exception(f"Unexpected token at position {self.pos}")

    def parse_unary(self):
        if op := self.match(token_types_list['MINUS']):
            return UnaryOperationNode(op, self.parse_unary())
        return self.parse_primary()

    def parse_term(self):
        node = self.parse_unary()
        while op := self.match(token_types_list['MULTIPLY'], token_types_list['DIVIDE'], token_types_list['MODULO']):
            node = BinOperationNode(op, node, self.parse_unary())
        return node

    def parse_formula(self):
        node = self.parse_term()
        while op := self.match(token_types_list['PLUS'], token_types_list['MINUS']):
            node = BinOperationNode(op, node, self.parse_term())
        return node

    def parse_comparison(self):
        node = self.parse_formula()
        while op := self.match(
            token_types_list['EQUAL'], token_types_list['NOT_EQUAL'],
            token_types_list['LESS'], token_types_list['LESS_EQUAL'],
            token_types_list['GREATER'], token_types_list['GREATER_EQUAL']
        ):
            node = BinOperationNode(op, node, self.parse_formula())
        return node

    def parse_assignment(self):
        node = self.parse_comparison()
        if isinstance(node, VariableNode) and (op := self.match(token_types_list['ASSIGN'])):
            return AssignNode(op, node, self.parse_assignment())
        return node

    def parse_expression(self):
        return self.parse_assignment()

    def parse_print(self):
        if self.match(token_types_list['PRINT']):
            expr = self.parse_expression()
            self.require(token_types_list['SEMICOLON'])
            return PrintNode(expr)
        return None

    def parse_return(self):
        if self.match(token_types_list['RETURN']):
            if self.match(token_types_list['SEMICOLON']):
                return ReturnNode(None)
            expr = self.parse_expression()
            self.require(token_types_list['SEMICOLON'])
            return ReturnNode(expr)
        return None

    def parse_if(self):
        if self.match(token_types_list['IF']):
            self.require(token_types_list['LPAREN'])
            condition = self.parse_expression()
            self.require(token_types_list['RPAREN'])
            then_branch = self.parse_code_block()
            else_branch = None
            if self.match(token_types_list['ELSE']):
                else_branch = self.parse_code_block()
            return IfNode(condition, then_branch, else_branch)
        return None

    def parse_while(self):
        if self.match(token_types_list['WHILE']):
            self.require(token_types_list['LPAREN'])
            condition = self.parse_expression()
            self.require(token_types_list['RPAREN'])
            body = self.parse_code_block()
            return WhileNode(condition, body)
        return None

    def parse_for(self):
        if self.match(token_types_list['FOR']):
            self.require(token_types_list['LPAREN'])
            init = self.parse_expression()
            self.require(token_types_list['SEMICOLON'])
            cond = self.parse_expression()
            self.require(token_types_list['SEMICOLON'])
            step = self.parse_expression()
            self.require(token_types_list['RPAREN'])
            body = self.parse_code_block()
            return ForNode(init, cond, step, body)
        return None

    def parse_function(self):
        if self.match(token_types_list['FUNCTION']):
            name = self.require(token_types_list['VARIABLE'])
            self.require(token_types_list['LPAREN'])
            params = []
            if not self.match(token_types_list['RPAREN']):
                params.append(self.require(token_types_list['VARIABLE']))
                while self.match(token_types_list['COMMA']):
                    params.append(self.require(token_types_list['VARIABLE']))
                self.require(token_types_list['RPAREN'])
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
        self.require(token_types_list['LBRACE'])
        while not self.match(token_types_list['RBRACE']):
            stmt = self.parse_statement()
            if not isinstance(stmt, ReturnNode):
                self.require(token_types_list['SEMICOLON'])
            block.add_node(stmt)
        return block

    def parse_code(self):
        root = StatementsNode()
        while self.pos < len(self.tokens):
            stmt = self.parse_statement()
            if not isinstance(stmt, ReturnNode):
                self.require(token_types_list['SEMICOLON'])
            root.add_node(stmt)
        return root

    def run(self, node):
        if isinstance(node, NumberNode):
            return int(node.number.text)

        if isinstance(node, StringNode):
            s = node.string.value
            if s.startswith('"') and s.endswith('"'):
                s = s[1:-1]  
            elif s.startswith("'") and s.endswith("'"):
                s = s[1:-1] 
            return s


        if isinstance(node, BooleanNode):
            return node.boolean.type.name == token_types_list['TRUE'].name

        if isinstance(node, NullNode):
            return None

        if isinstance(node, UnaryOperationNode):
            op_name = node.operator.type.name
            operand = self.run(node.operand)
            if op_name == token_types_list['MINUS'].name:
                return -operand
            if op_name == token_types_list['LOG'].name:
                print(operand)
                return None

        if isinstance(node, BinOperationNode):
            op_name = node.operator.type.name
            left = self.run(node.left_node)
            right = self.run(node.right_node)
            if op_name == token_types_list['PLUS'].name:
                return left + right
            if op_name == token_types_list['MINUS'].name:
                return left - right
            if op_name == token_types_list['MULTIPLY'].name:
                return left * right
            if op_name == token_types_list['DIVIDE'].name:
                return left // right
            if op_name == token_types_list['MODULO'].name:
                return left % right
            if op_name == token_types_list['EQUAL'].name:
                return left == right
            if op_name == token_types_list['NOT_EQUAL'].name:
                return left != right
            if op_name == token_types_list['LESS'].name:
                return left < right
            if op_name == token_types_list['LESS_EQUAL'].name:
                return left <= right
            if op_name == token_types_list['GREATER'].name:
                return left > right
            if op_name == token_types_list['GREATER_EQUAL'].name:
                return left >= right

        if isinstance(node, VariableNode):
            var_name = node.variable.value
            if var_name in self.scope:
                return self.scope[var_name]
            raise Exception(f"Variable '{var_name}' not found")

        if isinstance(node, AssignNode):
            var_name = node.variable.variable.value
            value = self.run(node.expression)
            self.scope[var_name] = value
            return value

        if isinstance(node, PrintNode):
            value = self.run(node.expression)
            print(value)
            return None

        if isinstance(node, FunctionCallNode):
            func_name = node.func.variable.value
            if func_name not in self.scope:
                raise Exception(f"Function '{func_name}' not found")
            func = self.scope[func_name]
            args = [self.run(arg) for arg in node.args]
            if callable(func):
                return func(args)
            raise Exception(f"'{func_name}' is not callable")

        if isinstance(node, StatementsNode):
            for stmt in node.code_strings:
                res = self.run(stmt)
                if isinstance(stmt, ReturnNode):
                    return res
            return None

        if isinstance(node, ReturnNode):
            if node.expression:
                return self.run(node.expression)
            return None

        if isinstance(node, FunctionDefNode):
            def func(args):
                local_scope = dict(self.scope)
                for param, arg in zip(node.params, args):
                    local_scope[param.text] = arg
                parser = Parser([])
                parser.scope = local_scope
                return parser.run(node.body)
            self.scope[node.name.text] = func
            return None

        if isinstance(node, IfNode):
            cond = self.run(node.condition)
            if cond:
                return self.run(node.then_branch)
            elif node.else_branch:
                return self.run(node.else_branch)
            return None

        if isinstance(node, WhileNode):
            while self.run(node.condition):
                res = self.run(node.body)
                if isinstance(res, ReturnNode):
                    return res
            return None

        if isinstance(node, ForNode):
            self.run(node.init)
            while self.run(node.cond):
                res = self.run(node.body)
                if isinstance(res, ReturnNode):
                    return res
                self.run(node.step)
            return None

        raise Exception(f"Unknown node type: {type(node)}")
