from abc import ABC
from typing import List, Optional, Callable, Any
from .token import Token, TokenType, token_types
from .ast import *
from .error import format_error

class Interpreter:
    """Interprets an AST for a strongly-typed language with Python-like imports."""
    def __init__(self, source: str, filename: str):
        self.source = source
        self.filename = filename
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.interfaces = {}
        self.enums = {}
        self.call_stack = [self.variables]
        self.imports = {}
        self.current_class = None
        self.super_class_stack = []

    def push_scope(self):
        self.call_stack.append({})
        self.variables = self.call_stack[-1]

    def pop_scope(self):
        self.call_stack.pop()
        self.variables = self.call_stack[-1] if self.call_stack else {}

    def interpret(self, node: ExpressionNode) -> Any:
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
            return float(node.value) if '.' in node.value or 'e' in node.value.lower() else int(node.value)
        elif isinstance(node, StringNode):
            return node.value[1:-1]  # Remove surrounding quotes
        elif isinstance(node, CharNode):
            return node.value[1:-1]  # Remove surrounding single quotes
        elif isinstance(node, BooleanNode):
            return node.value == 'true'
        elif isinstance(node, NullNode):
            return None
        elif isinstance(node, VariableNode):
            return self.get_variable(node.variable.value, node.variable.line, node.variable.column)
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
        elif isinstance(node, MemberCallNode):
            return self.interpret_member_call(node)
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
        elif isinstance(node, ThisNode):
            return self.interpret_this(node)
        elif isinstance(node, SuperNode):
            return self.interpret_super(node)
        raise RuntimeError(format_error(
            "RuntimeError",
            f"Unknown node type: {type(node)}",
            self.filename,
            self.source,
            getattr(node, 'line', 1),
            getattr(node, 'column', 1)
        ))

    def get_variable(self, name: str, line: int, column: int) -> Any:
        for scope in reversed(self.call_stack):
            if name in scope:
                return scope[name]
        raise RuntimeError(format_error(
            "RuntimeError",
            f"Undefined variable: {name}",
            self.filename,
            self.source,
            line,
            column
        ))

    def set_variable(self, name: str, value: Any, line: int, column: int) -> Any:
        for scope in reversed(self.call_stack):
            if name in scope:
                scope[name] = value
                return value
        raise RuntimeError(format_error(
            "RuntimeError",
            f"Undefined variable: {name}",
            self.filename,
            self.source,
            line,
            column
        ))

    def interpret_import(self, node: ImportNode) -> None:
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
        value = self.interpret(node.expression)
        return self.set_variable(node.variable.variable.value, value, node.variable.variable.line, node.variable.variable.column)

    def interpret_var_declaration(self, node: VarDeclarationNode) -> Any:
        value = self.interpret(node.expr) if node.expr else None
        if node.type_token:
            self.check_type(value, node.type_token(False))
        self.check_modifiers(node.modifiers, node.variable.variable.line, node.variable.variable.column)
        self.variables[node.variable.variable.value] = value
        return value

    def interpret_val_declaration(self, node: ValDeclarationNode) -> Any:
        value = self.interpret(node.expr)
        if node.type_token:
            self.check_type(value, node.type_token(False))
        self.check_modifiers(node.modifiers, node.variable.variable.line, node.variable.variable.column)
        self.variables[node.variable.variable.value] = value
        return value

    def interpret_const_declaration(self, node: ConstDeclarationNode) -> Any:
        value = self.interpret(node.expr)
        if node.type_token:
            self.check_type(value, node.type_token(False))
        self.check_modifiers(node.modifiers, node.variable.variable.line, node.variable.variable.column)
        self.variables[node.variable.variable.value] = value
        return value

    def check_modifiers(self, modifiers: List[Token], line: int, column: int) -> None:
        if not self.current_class:
            for mod in modifiers:
                if mod.value in ('private', 'protected'):
                    raise RuntimeError(format_error(
                        "RuntimeError",
                        f"Modifier '{mod.value}' is only allowed inside classes",
                        self.filename,
                        self.source,
                        line,
                        column
                    ))
        else:
            for mod in modifiers:
                if mod.value == 'protected' and not any(self.current_class in super_class for super_class in self.super_class_stack):
                    raise RuntimeError(format_error(
                        "RuntimeError",
                        "Protected access is only allowed within the class or its subclasses",
                        self.filename,
                        self.source,
                        line,
                        column
                    ))

    def check_type(self, value: Any, type_token: Token) -> None:
        expected_type = type_token.value
        if expected_type == 'str':
            expected_type = 'string'
        if value is None and expected_type != 'void':
            if not getattr(type_token, 'is_nullable', False):
                raise TypeError(format_error(
                    "TypeError",
                    f"Expected {expected_type}, got None",
                    self.filename,
                    self.source,
                    type_token.line,
                    type_token.column
                ))
            return
        if expected_type == 'float' or expected_type == 'double':
            if isinstance(value, (int, float)):
                return
            raise TypeError(format_error(
                "TypeError",
                f"Expected {expected_type}, got {type(value).__name__}",
                self.filename,
                self.source,
                type_token.line,
                type_token.column
            ))
        elif expected_type == 'int':
            if isinstance(value, int):
                return
            raise TypeError(format_error(
                "TypeError",
                f"Expected int, got {type(value).__name__}",
                self.filename,
                self.source,
                type_token.line,
                type_token.column
            ))
        elif expected_type == 'string':
            if isinstance(value, str):
                return
            raise TypeError(format_error(
                "TypeError",
                f"Expected string, got {type(value).__name__}",
                self.filename,
                self.source,
                type_token.line,
                type_token.column
            ))
        elif expected_type == 'boolean':
            if isinstance(value, bool):
                return
            raise TypeError(format_error(
                "TypeError",
                f"Expected boolean, got {type(value).__name__}",
                self.filename,
                self.source,
                type_token.line,
                type_token.column
            ))
        elif expected_type == 'void':
            if value is None:
                return
            raise TypeError(format_error(
                "TypeError",
                f"Expected void, got {type(value).__name__}",
                self.filename,
                self.source,
                type_token.line,
                type_token.column
            ))
        elif expected_type == 'any':
            return
        elif type_token.type.name == 'VARIABLE':
            if isinstance(value, dict) and value.get('__class__') == expected_type:
                return
            raise TypeError(format_error(
                "TypeError",
                f"Expected class {expected_type}, got {type(value).__name__}",
                self.filename,
                self.source,
                type_token.line,
                type_token.column
            ))
        else:
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Unknown type: {expected_type}",
                self.filename,
                self.source,
                type_token.line,
                type_token.column
            ))

    def interpret_binary_op(self, node: BinaryOperationNode) -> Any:
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
                    raise RuntimeError(format_error(
                        "RuntimeError",
                        "Division by zero",
                        self.filename,
                        self.source,
                        node.operator.line,
                        node.operator.column
                    ))
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
                return bool(left) and bool(right)
            elif op == 'OR':
                return bool(left) or bool(right)
            elif op == 'BIT_AND':
                if isinstance(left, int) and isinstance(right, int):
                    return left & right
                raise TypeError(format_error(
                    "TypeError",
                    "Bitwise AND requires integers",
                    self.filename,
                    self.source,
                    node.operator.line,
                    node.operator.column
                ))
            elif op == 'BIT_OR':
                if isinstance(left, int) and isinstance(right, int):
                    return left | right
                raise TypeError(format_error(
                    "TypeError",
                    "Bitwise OR requires integers",
                    self.filename,
                    self.source,
                    node.operator.line,
                    node.operator.column
                ))
            elif op == 'BIT_XOR':
                if isinstance(left, int) and isinstance(right, int):
                    return left ^ right
                raise TypeError(format_error(
                    "TypeError",
                    "Bitwise XOR requires integers",
                    self.filename,
                    self.source,
                    node.operator.line,
                    node.operator.column
                ))
            elif op == 'SHL':
                if isinstance(left, int) and isinstance(right, int):
                    return left << right
                raise TypeError(format_error(
                    "TypeError",
                    "Left shift requires integers",
                    self.filename,
                    self.source,
                    node.operator.line,
                    node.operator.column
                ))
            elif op == 'SHR':
                if isinstance(left, int) and isinstance(right, int):
                    return left >> right
                raise TypeError(format_error(
                    "TypeError",
                    "Right shift requires integers",
                    self.filename,
                    self.source,
                    node.operator.line,
                    node.operator.column
                ))
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Unknown operator: {op}",
                self.filename,
                self.source,
                node.operator.line,
                node.operator.column
            ))
        except TypeError as e:
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Type error in operation {op}: {str(e)}",
                self.filename,
                self.source,
                node.operator.line,
                node.operator.column
            ))

    def interpret_unary_op(self, node: UnaryOperationNode) -> Any:
        operand = self.interpret(node.operand)
        op = node.operator.type.name
        if node.is_postfix:
            if not isinstance(node.operand, VariableNode):
                raise RuntimeError(format_error(
                    "RuntimeError",
                    "Postfix operator requires a variable",
                    self.filename,
                    self.source,
                    node.operator.line,
                    node.operator.column
                ))
            var_name = node.operand.variable.value
            old_value = self.get_variable(var_name, node.operand.variable.line, node.operand.variable.column)
            if not isinstance(old_value, (int, float)):
                raise TypeError(format_error(
                    "TypeError",
                    f"Postfix operator requires numeric value, got {type(old_value).__name__}",
                    self.filename,
                    self.source,
                    node.operator.line,
                    node.operator.column
                ))
            if op == 'INCREMENT':
                self.set_variable(var_name, old_value + 1, node.operand.variable.line, node.operand.variable.column)
                return old_value
            elif op == 'DECREMENT':
                self.set_variable(var_name, old_value - 1, node.operand.variable.line, node.operand.variable.column)
                return old_value
        try:
            if op == 'MINUS':
                return -operand
            elif op == 'NOT':
                return not operand
            elif op == 'BIT_NOT':
                if isinstance(operand, int):
                    return ~operand
                raise TypeError(format_error(
                    "TypeError",
                    "Bitwise NOT requires an integer",
                    self.filename,
                    self.source,
                    node.operator.line,
                    node.operator.column
                ))
            elif op == 'INCREMENT':
                if not isinstance(operand, (int, float)):
                    raise TypeError(format_error(
                        "TypeError",
                        f"Increment requires numeric value, got {type(operand).__name__}",
                        self.filename,
                        self.source,
                        node.operator.line,
                        node.operator.column
                    ))
                return operand + 1
            elif op == 'DECREMENT':
                if not isinstance(operand, (int, float)):
                    raise TypeError(format_error(
                        "TypeError",
                        f"Decrement requires numeric value, got {type(operand).__name__}",
                        self.filename,
                        self.source,
                        node.operator.line,
                        node.operator.column
                    ))
                return operand - 1
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Unknown unary operator: {op}",
                self.filename,
                self.source,
                node.operator.line,
                node.operator.column
            ))
        except TypeError as e:
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Type error in unary operation {op}: {str(e)}",
                self.filename,
                self.source,
                node.operator.line,
                node.operator.column
            ))

    def interpret_null_coalesce(self, node: NullCoalesceNode) -> Any:
        left = self.interpret(node.left_node)
        return left if left is not None else self.interpret(node.right_node)

    def interpret_elvis(self, node: ElvisNode) -> Any:
        left = self.interpret(node.left_node)
        return left if left is not None else self.interpret(node.right_node)

    def interpret_if(self, node: IfNode) -> Any:
        condition = self.interpret(node.condition)
        if not isinstance(condition, bool):
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Condition must be boolean, got {type(condition).__name__}",
                self.filename,
                self.source,
                getattr(node.condition, 'line', 1),
                getattr(node.condition, 'column', 1)
            ))
        if condition:
            return self.interpret(node.then_branch)
        elif node.else_branch:
            return self.interpret(node.else_branch)
        return None

    def interpret_while(self, node: WhileNode) -> Any:
        while True:
            condition = self.interpret(node.condition)
            if not isinstance(condition, bool):
                raise RuntimeError(format_error(
                    "RuntimeError",
                    f"Condition must be boolean, got {type(condition).__name__}",
                    self.filename,
                    self.source,
                    getattr(node.condition, 'line', 1),
                    getattr(node.condition, 'column', 1)
                ))
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
                raise RuntimeError(format_error(
                    "RuntimeError",
                    f"Condition must be boolean, got {type(condition).__name__}",
                    self.filename,
                    self.source,
                    getattr(node.condition, 'line', 1),
                    getattr(node.condition, 'column', 1)
                ))
            if not condition:
                break
        return None

    def interpret_for(self, node: ForNode) -> Any:
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
        value = self.interpret(node.expression)
        for case in node.cases:
            case_value = self.interpret(case.value)
            if value == case_value:
                return self.interpret(case.body)
        if node.default:
            return self.interpret(node.default)
        return None

    def interpret_try(self, node: TryNode) -> Any:
        try:
            return self.interpret(node.try_block)
        except RuntimeError as e:
            for catch in node.catches:
                self.push_scope()
                try:
                    self.variables[catch.exception_var.variable.value] = str(e)
                    if catch.type_token:
                        self.check_type(str(e), catch.type_token(False))
                    return self.interpret(catch.body)
                finally:
                    self.pop_scope()
            raise
        finally:
            if node.finally_block:
                self.interpret(node.finally_block)

    def interpret_throw(self, node: ThrowNode) -> None:
        value = self.interpret(node.expression)
        raise RuntimeError(format_error(
            "RuntimeError",
            str(value),
            self.filename,
            self.source,
            getattr(node.expression, 'line', 1),
            getattr(node.expression, 'column', 1)
        ))

    def interpret_function_def(self, node: FunctionDefNode) -> None:
        self.check_modifiers(node.modifiers, node.name.line, node.name.column)
        self.functions[node.name.value] = node
        return None

    def interpret_function_call(self, node: FunctionCallNode) -> Any:
        func_name = node.func.variable.value
        if func_name not in self.functions:
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Undefined function: {func_name}",
                self.filename,
                self.source,
                node.func.variable.line,
                node.func.variable.column
            ))
        func = self.functions[func_name]
        self.check_modifiers(func.modifiers, node.func.variable.line, node.func.variable.column)
        args = [self.interpret(arg) for arg in node.args]
        if len(args) != len(func.params):
            raise TypeError(format_error(
                "TypeError",
                f"Expected {len(func.params)} arguments, got {len(args)}",
                self.filename,
                self.source,
                node.func.variable.line,
                node.func.variable.column
            ))
        self.push_scope()
        try:
            for param, arg in zip(func.params, args):
                if param.type_token:
                    self.check_type(arg, param.type_token(False))
                if arg is None and not param.is_nullable:
                    raise RuntimeError(format_error(
                        "RuntimeError",
                        f"Parameter {param.name.value} is not nullable",
                        self.filename,
                        self.source,
                        param.name.line,
                        param.name.column
                    ))
                self.variables[param.name.value] = arg
            result = self.interpret(func.body)
            if isinstance(result, ReturnNode):
                return_value = self.interpret_return(result)
                if func.return_type:
                    self.check_type(return_value, func.return_type(False))
                return return_value
            if func.return_type and func.return_type(False).value != 'void':
                raise RuntimeError(format_error(
                    "RuntimeError",
                    f"Function {func_name} must return a value of type {func.return_type(False).value}",
                    self.filename,
                    self.source,
                    node.func.variable.line,
                    node.func.variable.column
                ))
            return None
        finally:
            self.pop_scope()

    def interpret_member_call(self, node: MemberCallNode) -> Any:
        obj = self.interpret(node.obj)
        if not isinstance(obj, dict) or '__class__' not in obj:
            raise RuntimeError(format_error(
                "RuntimeError",
                "Member call requires an object",
                self.filename,
                self.source,
                node.method.variable.line,
                node.method.variable.column
            ))
        class_name = obj['__class__']
        if class_name not in self.classes:
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Undefined class: {class_name}",
                self.filename,
                self.source,
                node.method.variable.line,
                node.method.variable.column
            ))
        class_def = self.classes[class_name]
        method_name = node.method.variable.value
        method = None
        for member in class_def.members:
            if isinstance(member, FunctionDefNode) and member.name.value == method_name:
                method = member
                break
        if not method:
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Undefined method {method_name} in class {class_name}",
                self.filename,
                self.source,
                node.method.variable.line,
                node.method.variable.column
            ))
        self.check_modifiers(method.modifiers, node.method.variable.line, node.method.variable.column)
        args = [self.interpret(arg) for arg in node.args]
        if len(args) != len(method.params):
            raise TypeError(format_error(
                "TypeError",
                f"Expected {len(method.params)} arguments, got {len(args)}",
                self.filename,
                self.source,
                node.method.variable.line,
                node.method.variable.column
            ))
        self.push_scope()
        try:
            for param, arg in zip(method.params, args):
                if param.type_token:
                    self.check_type(arg, param.type_token(False))
                if arg is None and not param.is_nullable:
                    raise RuntimeError(format_error(
                        "RuntimeError",
                        f"Parameter {param.name.value} is not nullable",
                        self.filename,
                        self.source,
                        param.name.line,
                        param.name.column
                    ))
                self.variables[param.name.value] = arg
            self.variables['this'] = obj
            result = self.interpret(method.body)
            if isinstance(result, ReturnNode):
                return_value = self.interpret_return(result)
                if method.return_type:
                    self.check_type(return_value, method.return_type(False))
                return return_value
            return None
        finally:
            self.pop_scope()

    def interpret_lambda(self, node: LambdaNode) -> Any:
        def lambda_func(*args):
            if len(args) != len(node.params):
                raise TypeError(format_error(
                    "TypeError",
                    f"Expected {len(node.params)} arguments, got {len(args)}",
                    self.filename,
                    self.source,
                    node.params[0].line if node.params else 1,
                    node.params[0].column if node.params else 1
                ))
            self.push_scope()
            try:
                for param, arg in zip(node.params, args):
                    if param.type_token:
                        self.check_type(arg, param.type_token(False))
                    if arg is None and not param.is_nullable:
                        raise RuntimeError(format_error(
                            "RuntimeError",
                            f"Parameter {param.name.value} is not nullable",
                            self.filename,
                            self.source,
                            param.name.line,
                            param.name.column
                        ))
                    self.variables[param.name.value] = arg
                return self.interpret(node.body)
            finally:
                self.pop_scope()
        return lambda_func

    def interpret_class_def(self, node: ClassNode) -> None:
        prev_class = self.current_class
        self.current_class = node.name.value
        self.classes[node.name.value] = node
        if node.superclass:
            superclass_name = node.superclass.variable.value
            if superclass_name not in self.classes:
                raise RuntimeError(format_error(
                    "RuntimeError",
                    f"Undefined superclass: {superclass_name}",
                    self.filename,
                    self.source,
                    node.superclass.variable.line,
                    node.superclass.variable.column
                ))
            self.super_class_stack.append(superclass_name)
        for interface in node.interfaces:
            interface_name = interface.variable.value
            if interface_name not in self.interfaces:
                raise RuntimeError(format_error(
                    "RuntimeError",
                    f"Undefined interface: {interface_name}",
                    self.filename,
                    self.source,
                    interface.variable.line,
                    interface.variable.column
                ))
        for member in node.members:
            if isinstance(member, (VarDeclarationNode, ValDeclarationNode, ConstDeclarationNode, FunctionDefNode)):
                self.interpret(member)
        self.current_class = prev_class
        if node.superclass:
            self.super_class_stack.pop()
        return None

    def interpret_interface_def(self, node: InterfaceNode) -> None:
        self.interfaces[node.name.value] = node
        return None

    def interpret_enum_def(self, node: EnumNode) -> None:
        self.enums[node.name.value] = node
        for value in node.values:
            self.variables[value.value] = value.value
        for member in node.members:
            self.interpret(member)
        return None

    def interpret_return(self, node: ReturnNode) -> Any:
        return self.interpret(node.expression) if node.expression else None

    def interpret_print(self, node: PrintNode) -> None:
        value = self.interpret(node.expression)
        print(value)
        return None

    def interpret_instanceof(self, node: InstanceOfNode) -> bool:
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
        class_name = node.type_token.value
        if class_name not in self.classes:
            raise RuntimeError(format_error(
                "RuntimeError",
                f"Undefined class: {class_name}",
                self.filename,
                self.source,
                node.type_token.line,
                node.type_token.column
            ))
        class_def = self.classes[class_name]
        args = [self.interpret(arg) for arg in node.args]
        instance = {'__class__': class_name}
        self.push_scope()
        try:
            self.variables['this'] = instance
            for member in class_def.members:
                if isinstance(member, (VarDeclarationNode, ValDeclarationNode, ConstDeclarationNode)):
                    self.interpret(member)
                    instance[member.variable.variable.value] = self.variables[member.variable.variable.value]
        finally:
            self.pop_scope()
        return instance

    def interpret_block(self, node: BlockNode) -> Any:
        self.push_scope()
        try:
            for stmt in node.statements:
                result = self.interpret(stmt)
                if isinstance(result, (ReturnNode, BreakNode, ContinueNode)):
                    return result
            return None
        finally:
            self.pop_scope()

    def interpret_this(self, node: ThisNode) -> Any:
        if not self.current_class:
            raise RuntimeError(format_error(
                "RuntimeError",
                "'this' can only be used inside a class",
                self.filename,
                self.source,
                node.token.line,
                node.token.column
            ))
        return self.get_variable('this', node.token.line, node.token.column)

    def interpret_super(self, node: SuperNode) -> Any:
        if not self.current_class or not self.super_class_stack:
            raise RuntimeError(format_error(
                "RuntimeError",
                "'super' can only be used inside a class with a superclass",
                self.filename,
                self.source,
                node.token.line,
                node.token.column
            ))
        this_obj = self.get_variable('this', node.token.line, node.token.column)
        superclass_name = self.super_class_stack[-1]
        return {'__class__': superclass_name, **this_obj}