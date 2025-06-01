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
    def __init__(self, value: Token):
        self.value = value

    def __repr__(self):
        return f"BooleanNode({self.value})"


class NullNode(ExpressionNode):
    def __init__(self, token: Token):
        self.token = token

    def __repr__(self):
        return f"NullNode({self.token})"


class VariableNode(ExpressionNode):
    def __init__(self, variable: Token):
        self.variable = variable

    def __repr__(self):
        return f"VariableNode({self.variable})"


class AssignNode(ExpressionNode):
    def __init__(self, operator: Token, left_node: ExpressionNode, right_node: ExpressionNode):
        self.operator = operator
        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self):
        return f"AssignNode({self.left_node}, {self.operator}, {self.right_node})"


class BinOperationNode(ExpressionNode):
    def __init__(self, operator: Token, left_node: ExpressionNode, right_node: ExpressionNode):
        self.operator = operator
        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self):
        return f"BinOperationNode({self.left_node}, {self.operator}, {self.right_node})"


class UnaryOperationNode(ExpressionNode):
    def __init__(self, operator: Token, operand: ExpressionNode):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOperationNode({self.operator}, {self.operand})"


class IfNode(ExpressionNode):
    def __init__(
        self,
        condition: ExpressionNode,
        then_branch: 'StatementsNode',
        else_branch: Optional['StatementsNode'] = None,
    ):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"IfNode({self.condition}, then={self.then_branch}, else={self.else_branch})"


class WhileNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, body: 'StatementsNode'):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileNode({self.condition}, {self.body})"


class ForNode(ExpressionNode):
    def __init__(
        self,
        init: ExpressionNode,
        condition: ExpressionNode,
        step: ExpressionNode,
        body: 'StatementsNode',
    ):
        self.init = init
        self.condition = condition
        self.step = step
        self.body = body

    def __repr__(self):
        return (
            f"ForNode(init={self.init}, cond={self.condition}, "
            f"step={self.step}, body={self.body})"
        )


class PrintNode(ExpressionNode):
    def __init__(self, value: ExpressionNode):
        self.value = value

    def __repr__(self):
        return f"PrintNode({self.value})"


class ReturnNode(ExpressionNode):
    def __init__(self, value: Optional[ExpressionNode]):
        self.value = value

    def __repr__(self):
        return f"ReturnNode({self.value})"


class FunctionDefNode(ExpressionNode):
    def __init__(self, name: Token, parameters: List[Token], body: 'StatementsNode'):
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self):
        return f"FunctionDefNode(name={self.name}, params={self.parameters}, body={self.body})"


class FunctionCallNode(ExpressionNode):
    def __init__(self, function_node, args):
        self.func = function_node
        self.args = args

    def __repr__(self):
        return f"FunctionCallNode({self.callee}, args={self.arguments})"


class StatementsNode(ExpressionNode):
    def __init__(self):
        self.code_strings: List[ExpressionNode] = []

    def add_node(self, node: ExpressionNode):
        self.code_strings.append(node)

    def __repr__(self):
        return f"StatementsNode({self.code_strings})"
