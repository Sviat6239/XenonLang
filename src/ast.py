from abc import ABC
from typing import List, Optional
from .token import Token


class ExpressionNode(ABC):
    pass


class NumberNode(ExpressionNode):
    def __init__(self, number: Token):
        self.number = number

    def __repr__(self):
        return f"NumberNode({self.number})"


class StringNode(ExpressionNode):
    def __init__(self, string: Token):
        self.string = string

    def __repr__(self):
        return f"StringNode({self.string})"


class BooleanNode(ExpressionNode):
    def __init__(self, boolean: Token):
        self.boolean = boolean

    def __repr__(self):
        return f"BooleanNode({self.boolean})"


class NullNode(ExpressionNode):
    def __init__(self, null: Token):
        self.null = null

    def __repr__(self):
        return f"NullNode({self.null})"


class UnaryOperationNode(ExpressionNode):
    def __init__(self, operator: Token, operand: ExpressionNode):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOperationNode({self.operator}, {self.operand})"


class BinOperationNode(ExpressionNode):
    def __init__(self, operator: Token, left_node: ExpressionNode, right_node: ExpressionNode):
        self.operator = operator
        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self):
        return f"BinOperationNode({self.operator}, {self.left_node}, {self.right_node})"


class VariableNode(ExpressionNode):
    def __init__(self, variable: Token):
        self.variable = variable

    def __repr__(self):
        return f"VariableNode({self.variable})"


class AssignNode(ExpressionNode):
    def __init__(self, token: Token, variable: VariableNode, expression: ExpressionNode):
        self.token = token
        self.variable = variable
        self.expression = expression

    def __repr__(self):
        return f"AssignNode({self.token}, {self.variable}, {self.expression})"


class PrintNode(ExpressionNode):
    def __init__(self, expression: ExpressionNode):
        self.expression = expression

    def __repr__(self):
        return f"PrintNode({self.expression})"


class FunctionCallNode(ExpressionNode):
    def __init__(self, func: VariableNode, args: List[ExpressionNode]):
        self.func = func
        self.args = args

    def __repr__(self):
        return f"FunctionCallNode({self.func}, {self.args})"


class ReturnNode(ExpressionNode):
    def __init__(self, expression: Optional[ExpressionNode]):
        self.expression = expression

    def __repr__(self):
        return f"ReturnNode({self.expression})"


class FunctionDefNode(ExpressionNode):
    def __init__(self, name: Token, params: List[Token], body: 'StatementsNode'):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"FunctionDefNode({self.name}, {self.params}, {self.body})"


class IfNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, then_branch: 'StatementsNode', else_branch: Optional['StatementsNode']):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"IfNode({self.condition}, {self.then_branch}, {self.else_branch})"


class WhileNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, body: 'StatementsNode'):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileNode({self.condition}, {self.body})"


class ForNode(ExpressionNode):
    def __init__(self, init: ExpressionNode, cond: ExpressionNode, step: ExpressionNode, body: 'StatementsNode'):
        self.init = init
        self.cond = cond
        self.step = step
        self.body = body

    def __repr__(self):
        return f"ForNode({self.init}, {self.cond}, {self.step}, {self.body})"


class StatementsNode(ExpressionNode):
    def __init__(self):
        self.code_strings: List[ExpressionNode] = []

    def add_node(self, node: ExpressionNode):
        self.code_strings.append(node)

    def __repr__(self):
        return f"StatementsNode({self.code_strings})"
