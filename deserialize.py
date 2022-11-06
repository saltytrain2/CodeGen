import sys
from typing import List, Any, Callable, Tuple
from coolast import *

__all__ = ["read_ast"]

# recursive approach to writing parsing results to ast
def read_line(ast:List[str]) -> str:
    return ast.pop()


def read_list(ast:List[str], elem_fn:Callable[[List[str]], Any]) -> List[Any]:
    # Follow the spec to read a generic list
    list = []
    for _ in range(int(read_line(ast))):
        list.append(elem_fn(ast))
    
    return list
        

def read_identifier(ast:List[str]) -> Identifier:
    # Follow the spec to read an identifier
    lineno = read_line(ast)
    name = read_line(ast)
    return Identifier(lineno, name)
    

def read_let_binding(ast:List[str]) -> LetBinding:
    # Follow the spec to read a single let binding
    # Used when we write a let expression
    binding_type = read_line(ast)
    variable = read_identifier(ast)
    var_type = read_identifier(ast)
    init_expr = None
    if binding_type == "let_binding_init":
        init_expr = read_expr(ast)
    return LetBinding(variable, var_type, init_expr)


def read_case_element(ast:List[str]) -> CaseElement:
    # Follow the spec to read a case element
    # Used when we write a case expression
    formal = read_formal(ast)
    expr = read_expr(ast)
    return CaseElement(formal, expr)


def read_expr(ast:List[str]) -> Expression:
    # Determine type of expression printing style and call the appropriate function
    lineno = read_line(ast)
    expr_type = read_line(ast)
    expr_name = read_line(ast)
    if expr_name == "assign":
        var = read_identifier(ast)
        rhs = read_expr(ast)
        return Assign(lineno, var, rhs, expr_type)
    elif expr_name == "dynamic_dispatch":
        obj = read_expr(ast)
        method_name = read_identifier(ast)
        args = read_list(ast, read_expr)
        return DynamicDispatch(lineno, obj, method_name, args, expr_type)
    elif expr_name == "static_dispatch":
        obj = read_expr(ast)
        class_type = read_identifier(ast)
        method_name = read_identifier(ast)
        args = read_list(ast, read_expr)
        return StaticDispatch(lineno, obj, class_type, method_name, args, expr_type)
    elif expr_name == "self_dispatch":
        method_name = read_identifier(ast)
        args = read_list(ast, read_expr)
        return SelfDispatch(lineno, method_name, args, expr_type)
    elif expr_name == 'if':
        condition = read_expr(ast)
        then_body = read_expr(ast)
        else_body = read_expr(ast)
        return If(lineno, condition, then_body, else_body, expr_type)
    elif expr_name == 'while':
        condition = read_expr(ast)
        while_body = read_expr(ast)
        return While(lineno, condition, while_body, expr_type)
    elif expr_name == 'block':
        return Block(lineno, read_list(ast, read_expr), expr_type)
    elif expr_name == 'new':
        class_name = read_identifier(ast)
        return New(lineno, class_name, expr_type)
    elif expr_name == 'isvoid':
        rhs = read_expr(ast)
        return IsVoid(lineno, rhs, expr_type)
    elif expr_name == 'plus':
        lhs = read_expr(ast)
        rhs = read_expr(ast)
        return Plus(lineno, lhs, rhs, expr_type)
    elif expr_name == 'minus':
        lhs = read_expr(ast)
        rhs = read_expr(ast)
        return Minus(lineno, lhs, rhs, expr_type)
    elif expr_name == 'times':
        lhs = read_expr(ast)
        rhs = read_expr(ast)
        return Times(lineno, lhs, rhs, expr_type)
    elif expr_name == 'divide':
        lhs = read_expr(ast)
        rhs = read_expr(ast)
        return Divide(lineno, lhs, rhs, expr_type)
    elif expr_name == 'lt':
        lhs = read_expr(ast)
        rhs = read_expr(ast)
        return Lt(lineno, lhs, rhs, expr_type)
    elif expr_name == 'le':
        lhs = read_expr(ast)
        rhs = read_expr(ast)
        return Le(lineno, lhs, rhs, expr_type)
    elif expr_name == 'eq':
        lhs = read_expr(ast)
        rhs = read_expr(ast)
        return Eq(lineno, lhs, rhs, expr_type)
    elif expr_name == 'not':
        rhs = read_expr(ast)
        return Not(lineno, rhs, expr_type)
    elif expr_name == 'negate':
        rhs = read_expr(ast)
        return Negate(lineno, rhs, expr_type)
    elif expr_name == "let":
        binding_list = read_list(ast, read_let_binding)
        let_expr = read_expr(ast)
        return Let(lineno, binding_list, let_expr, expr_type)
    elif expr_name == "case":
        case_expr = read_expr(ast)
        case_list = read_list(ast, read_case_element)
        return Case(lineno, case_expr, case_list, expr_type)
    elif expr_name == "integer":
        return Integer(lineno, read_line(ast), expr_type)
    elif expr_name == "string":
        return StringExp(lineno, read_line(ast), expr_type)
    elif expr_name == "identifier":
        return Variable(lineno, read_identifier(ast), expr_type)
    elif expr_name == "true" or expr_name == "false":
        return Bool(lineno, expr_name, expr_type)
    elif expr_name == "internal":
        return Internal(expr_type, read_line(ast))


def read_feature(ast:List[str]) -> Feature:
    # Follow the spec to read a feature
    feature_type = read_line(ast)
    feature_name = read_identifier(ast)

    if feature_type == "attribute_no_init":
        attr_type = read_identifier(ast)
        return Attribute(feature_name, attr_type, None)
    elif feature_type == "attribute_init":
        attr_type = read_identifier(ast)
        feature_expr = read_expr(ast)
        return Attribute(feature_name, attr_type, feature_expr)
    elif feature_type == "method":
        formal_list = read_list(ast, read_formal)
        return_type = read_identifier(ast)
        feature_expr = read_expr(ast)
        return Method(feature_name, return_type, formal_list, feature_expr)


def read_formal(ast) -> Formal:
    # Follow the spec to read a formal
    name = read_identifier(ast)
    formal_type = read_identifier(ast)
    return Formal(name, formal_type)


def read_class(ast:List[str]) -> Class:
    # Follow the spec to read a class
    class_name = read_identifier(ast)
    inherit_status = read_line(ast)
    pred = None

    if inherit_status == "inherits":
        pred = read_identifier(ast)
    
    feature_list = read_list(ast, read_feature)
    return Class(class_name, pred, feature_list)


def read_class_attribute(ast:List[str]) -> ClassAttribute:
    attribute_kind = read_line(ast)
    attribute_name = read_line(ast)
    attribute_type = read_line(ast)
    attribute_expr = None

    if attribute_kind == "initializer":
        attribute_expr = read_expr(ast)

    return ClassAttribute(attribute_name, attribute_kind, attribute_type, attribute_expr)


def read_impl_method(ast:List[str]) -> ImplMethod:
    class_name = read_line(ast)
    formal_list = read_list(ast, read_line)
    method_parent = read_line(ast)
    method_expr = read_expr(ast)
    return ImplMethod(class_name, formal_list, method_parent, method_expr)
    

def read_class_map_entry(ast:List[str]) -> ClassMapEntry:
    class_name = read_line(ast)
    attr_list = read_list(ast, read_class_attribute)
    return ClassMapEntry(class_name, attr_list)


def read_impl_map_entry(ast:List[str]) -> ImplMapEntry:
    class_name = read_line(ast)
    method_list = read_list(ast, read_impl_method)
    return ImplMapEntry(class_name, method_list)


def read_parent_map_entry(ast:List[str]) -> ParentMapEntry:
    child = read_line(ast)
    parent = read_line(ast)
    return ParentMapEntry(parent, child)


def read_ast(ast:List[str]) -> Tuple[List[ClassMapEntry], List[ImplMapEntry], List[ParentMapEntry], List[Class]]:
    # Follow the spec to read a program
    read_line(ast)
    class_map = read_list(ast, read_class_map_entry)
    read_line(ast)
    impl_map = read_list(ast, read_impl_map_entry)
    read_line(ast)
    parent_map = read_list(ast, read_parent_map_entry)
    annotated_ast = read_list(ast, read_class)

    return class_map, impl_map, parent_map, annotated_ast


def main(argv):
    with open(argv[1], 'r') as file:
        ast_lines = [line.strip("\n\r") for line in reversed(file.readlines())]

    class_map, impl_map, parent_map, class_list = read_ast(ast_lines)
    with open(argv[1][:-8], "w") as file:
        file.write(f"class_map\n{len(class_map)}\n")
        for elem in class_map:
            file.write(repr(elem))
        
        file.write(f"implementation_map\n{len(impl_map)}\n")
        for elem in impl_map:
            file.write(repr(elem))
        
        file.write(f"parent_map\n{len(parent_map)}\n")
        for elem in parent_map:
            file.write(repr(elem))

        file.write(f"{len(class_list)}\n")
        for elem in class_list:
            file.write(repr(elem))

if __name__ == '__main__':
    main(sys.argv)
