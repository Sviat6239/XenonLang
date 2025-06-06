from abc import ABC
from typing import List, Optional, Any, Dict
from .token import Token, TokenType, token_types_list
from .ast import *

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
        """Checks if the value matches the expected type, allowing int-to-float conversion."""
        expected_type = type_token.value
        if value is None and expected_type != 'void':
            raise RuntimeError(f"Expected {expected_type}, got None")
        
        if expected_type == 'float' or expected_type == 'double':
            if isinstance(value, (int, float)):
                return  # Allow int or float for float/double
            raise RuntimeError(f"Expected {expected_type}, got {type(value).__name__}")
        elif expected_type == 'int':
            if isinstance(value, int):
                return
            raise RuntimeError(f"Expected int, got {type(value).__name__}")
        elif expected_type == 'string':
            if isinstance(value, str):
                return
            raise RuntimeError(f"Expected string, got {type(value).__name__}")
        elif expected_type == 'boolean':
            if isinstance(value, bool):
                return
            raise RuntimeError(f"Expected boolean, got {type(value).__name__}")
        else:
            raise RuntimeError(f"Unknown type: {expected_type}")

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

           