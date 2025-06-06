from abc import ABC
from typing import List, Optional, Callable
from .token import Token

class ExpressionNode(ABC):
    pass

# Literal Nodes
class NumberNode(ExpressionNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value  # Store the numeric value as a string

    def __repr__(self):
        return f"NumberNode(value={self.value})"

class StringNode(ExpressionNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value  # Store the string value with quotes

    def __repr__(self):
        return f"StringNode(value={self.value})"

class CharNode(ExpressionNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value  # Store the char value with single quotes

    def __repr__(self):
        return f"CharNode(value={self.value})"

class BooleanNode(ExpressionNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value  # Store the boolean value ("true" or "false")

    def __repr__(self):
        return f"BooleanNode(value={self.value})"

class NullNode(ExpressionNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value  # Store the null value ("null")

    def __repr__(self):
        return f"NullNode(value={self.value})"

# Operator Nodes
class UnaryOperationNode(ExpressionNode):
    def __init__(self, operator: Token, operand: ExpressionNode, is_postfix: bool = False):
        self.operator = operator
        self.operand = operand
        self.is_postfix = is_postfix

    def __repr__(self):
        return f"UnaryOperationNode(operator={self.operator}, operand={self.operand}, is_postfix={self.is_postfix})"

class BinaryOperationNode(ExpressionNode):
    def __init__(self, operator: Token, left_node: ExpressionNode, right_node: ExpressionNode):
        self.operator = operator
        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self):
        return f"BinaryOperationNode({self.operator}, {self.left_node}, {self.right_node})"

class NullCoalesceNode(ExpressionNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self):
        return f"NullCoalesceNode({self.left_node}, {self.right_node})"

class ElvisNode(ExpressionNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self):
        return f"ElvisNode({self.left_node}, {self.right_node})"

# Variable and Assignment Nodes
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

class VarDeclarationNode(ExpressionNode):
    def __init__(self, var_token: Token, variable: VariableNode, type_token: Optional[Callable[[bool], Token]], expr: Optional[ExpressionNode], modifiers: List[Token] = None):
        self.var_token = var_token
        self.variable = variable
        self.type_token = type_token
        self.expr = expr
        self.modifiers = modifiers or []

    def __repr__(self):
        return f"VarDeclarationNode({self.var_token}, {self.variable}, {self.type_token}, {self.expr}, modifiers={self.modifiers})"

class ValDeclarationNode(ExpressionNode):
    def __init__(self, val_token: Token, variable: VariableNode, type_token: Optional[Callable[[bool], Token]], expr: Optional[ExpressionNode], modifiers: List[Token] = None):
        self.val_token = val_token
        self.variable = variable
        self.type_token = type_token
        self.expr = expr
        self.modifiers = modifiers or []

    def __repr__(self):
        return f"ValDeclarationNode({self.val_token}, {self.variable}, {self.type_token}, {self.expr}, modifiers={self.modifiers})"

class ConstDeclarationNode(ExpressionNode):
    def __init__(self, const_token: Token, variable: VariableNode, type_token: Optional[Callable[[bool], Token]], expr: Optional[ExpressionNode], modifiers: List[Token] = None):
        self.const_token = const_token
        self.variable = variable
        self.type_token = type_token
        self.expr = expr
        self.modifiers = modifiers or []

    def __repr__(self):
        return f"ConstDeclarationNode({self.const_token}, {self.variable}, {self.type_token}, {self.expr}, modifiers={self.modifiers})"

# Control Flow Nodes
class IfNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, then_branch: 'BlockNode', else_branch: Optional['BlockNode']):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"IfNode({self.condition}, {self.then_branch}, {self.else_branch})"

class WhileNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, body: 'BlockNode'):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileNode({self.condition}, {self.body})"

class DoWhileNode(ExpressionNode):
    def __init__(self, body: 'BlockNode', condition: ExpressionNode):
        self.body = body
        self.condition = condition

    def __repr__(self):
        return f"DoWhileNode({self.body}, {self.condition})"

class ForNode(ExpressionNode):
    def __init__(self, init: Optional[ExpressionNode], cond: Optional[ExpressionNode], step: Optional[ExpressionNode], body: 'BlockNode'):
        self.init = init
        self.cond = cond
        self.step = step
        self.body = body

    def __repr__(self):
        return f"ForNode({self.init}, {self.cond}, {self.step}, {self.body})"

class SwitchNode(ExpressionNode):
    def __init__(self, expression: ExpressionNode, cases: List['CaseNode'], default: Optional['BlockNode']):
        self.expression = expression
        self.cases = cases
        self.default = default

    def __repr__(self):
        return f"SwitchNode({self.expression}, {self.cases}, {self.default})"

class CaseNode(ExpressionNode):
    def __init__(self, value: ExpressionNode, body: ExpressionNode):
        self.value = value
        self.body = body

    def __repr__(self):
        return f"CaseNode({self.value}, {self.body})"

class BreakNode(ExpressionNode):
    def __init__(self):
        pass

    def __repr__(self):
        return "BreakNode()"

class ContinueNode(ExpressionNode):
    def __init__(self):
        pass

    def __repr__(self):
        return "ContinueNode()"

# Exception Handling Nodes
class TryNode(ExpressionNode):
    def __init__(self, try_block: 'BlockNode', catches: List['CatchNode'], finally_block: Optional['BlockNode']):
        self.try_block = try_block
        self.catches = catches
        self.finally_block = finally_block

    def __repr__(self):
        return f"TryNode({self.try_block}, {self.catches}, {self.finally_block})"

class CatchNode(ExpressionNode):
    def __init__(self, exception_var: VariableNode, type_token: Optional[Callable[[bool], Token]], body: 'BlockNode'):
        self.exception_var = exception_var
        self.type_token = type_token
        self.body = body

    def __repr__(self):
        return f"CatchNode({self.exception_var}, {self.type_token}, {self.body})"

class ThrowNode(ExpressionNode):
    def __init__(self, expression: ExpressionNode):
        self.expression = expression

    def __repr__(self):
        return f"ThrowNode({self.expression})"

# Function and Lambda Nodes
class FunctionCallNode(ExpressionNode):
    def __init__(self, func: VariableNode, args: List[ExpressionNode]):
        self.func = func
        self.args = args

    def __repr__(self):
        return f"FunctionCallNode({self.func}, {self.args})"

class FunctionDefNode(ExpressionNode):
    def __init__(self, name: Token, params: List['ParamNode'], return_type: Optional[Callable[[bool], Token]], body: 'BlockNode', modifiers: List[Token] = None):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.modifiers = modifiers or []

    def __repr__(self):
        return f"FunctionDefNode({self.name}, {self.params}, {self.return_type}, {self.body}, modifiers={self.modifiers})"

class ParamNode(ExpressionNode):
    def __init__(self, name: Token, type_token: Optional[Callable[[bool], Token]], is_nullable: bool = False):
        self.name = name
        self.type_token = type_token
        self.is_nullable = is_nullable

    def __repr__(self):
        return f"ParamNode({self.name}, {self.type_token}, nullable={self.is_nullable})"

class LambdaNode(ExpressionNode):
    def __init__(self, params: List['ParamNode'], body: ExpressionNode):
        self.params = params
        self.body = body

    def __repr__(self):
        return f"LambdaNode({self.params}, {self.body})"

# Class and Interface Nodes
class ClassNode(ExpressionNode):
    def __init__(self, name: Token, superclass: Optional[VariableNode], interfaces: List[VariableNode], members: List[ExpressionNode], modifiers: List[Token] = None):
        self.name = name
        self.superclass = superclass
        self.interfaces = interfaces
        self.members = members
        self.modifiers = modifiers or []

    def __repr__(self):
        return f"ClassNode({self.name}, {self.superclass}, {self.interfaces}, {self.members}, modifiers={self.modifiers})"

class InterfaceNode(ExpressionNode):
    def __init__(self, name: Token, members: List[ExpressionNode], modifiers: List[Token] = None):
        self.name = name
        self.members = members
        self.modifiers = modifiers or []

    def __repr__(self):
        return f"InterfaceNode({self.name}, {self.members}, modifiers={self.modifiers})"

class EnumNode(ExpressionNode):
    def __init__(self, name: Token, values: List[Token], members: List[ExpressionNode]):
        self.name = name
        self.values = values
        self.members = members

    def __repr__(self):
        return f"EnumNode({self.name}, {self.values}, {self.members})"

# Other Nodes
class ReturnNode(ExpressionNode):
    def __init__(self, expression: Optional[ExpressionNode]):
        self.expression = expression

    def __repr__(self):
        return f"ReturnNode({self.expression})"

class PrintNode(ExpressionNode):
    def __init__(self, expression: ExpressionNode):
        self.expression = expression

    def __repr__(self):
        return f"PrintNode({self.expression})"

class InstanceOfNode(ExpressionNode):
    def __init__(self, expression: ExpressionNode, type_token: Token):
        self.expression = expression
        self.type_token = type_token

    def __repr__(self):
        return f"InstanceOfNode({self.expression}, {self.type_token})"

class NewNode(ExpressionNode):
    def __init__(self, type_token: Token, args: List[ExpressionNode]):
        self.type_token = type_token
        self.args = args

    def __repr__(self):
        return f"NewNode({self.type_token}, {self.args})"

# Instance Reference Nodes
class ThisNode(ExpressionNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value  # Store the 'this' keyword value

    def __repr__(self):
        return f"ThisNode(value={self.value})"

class SuperNode(ExpressionNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value  # Store the 'super' keyword value

    def __repr__(self):
        return f"SuperNode(value={self.value})"

class MemberCallNode(ExpressionNode):
    def __init__(self, obj: ExpressionNode, method: VariableNode, args: List[ExpressionNode]):
        self.obj = obj
        self.method = method
        self.args = args

    def __repr__(self):
        return f"MemberCallNode(obj={self.obj}, method={self.method}, args={self.args})"

# Import Node (Python-style)
class ImportNode(ExpressionNode):
    def __init__(self, module: List[Token], names: List[Token] = None, alias: Optional[Token] = None):
        self.module = module  # e.g., ['os', 'path'] for 'from os.path'
        self.names = names or []  # e.g., ['sin', 'cos'] for 'from math import sin, cos'
        self.alias = alias  # e.g., 'np' for 'import numpy as np'

    def __repr__(self):
        return f"ImportNode(module={self.module}, names={self.names}, alias={self.alias})"

# Block and Program Nodes
class BlockNode(ExpressionNode):
    def __init__(self, statements: List[ExpressionNode]):
        self.statements = statements

    def __repr__(self):
        return f"BlockNode({self.statements})"

class StatementsNode(ExpressionNode):
    def __init__(self):
        self.code_strings: List[ExpressionNode] = []

    def add_node(self, node: ExpressionNode):
        self.code_strings.append(node)

    def __repr__(self):
        return f"StatementsNode({self.code_strings})"

class ProgramNode(ExpressionNode):
    def __init__(self, imports: List['ImportNode'], statements: List[ExpressionNode]):
        self.imports = imports
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode({self.imports}, {self.statements})"