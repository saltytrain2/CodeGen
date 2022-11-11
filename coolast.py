from __future__ import annotations
from typing import List, Any, Dict, Set

class TypeCheckError(Exception):
    pass

class Identifier:
    def __init__(self, lineno:str, name:str):
        self.lineno = lineno
        self.name = name
    
    def __repr__(self) -> str:
        return f"{self.lineno}\n{self.name}\n"
    
    def get_lineno(self) -> str:
        return self.lineno
    
    def get_name(self) -> str:
        return self.name


class Formal:
    def __init__(self, name:Identifier, formal_type:Identifier):
        self.name_id = name
        self.type_id = formal_type

    def __repr__(self) -> str:
        return f"{repr(self.name_id)}{repr(self.type_id)}"

    def get_name(self) -> str:
        return self.name_id.get_name()

    def get_type(self) -> str:
        return self.type_id.get_name()

    def get_name_lineno(self) -> str:
        return self.name_id.get_lineno()

    def get_type_lineno(self) -> str:
        return self.type_id.get_lineno()


class Expression:
    def __init__(self, lineno:str, kind:str, exp_type:str=None):
        self.lineno = lineno
        self.kind = kind
        self.exp_type = exp_type

    def __repr__(self) -> str:
        type_str = self.exp_type + "\n" if self.exp_type is not None else ""
        if len(type_str) > 10 and type_str[:10] == "SELF_TYPE@":
            type_str = "SELF_TYPE\n"
        return f"{self.lineno}\n{type_str}{self.kind}\n"

    def get_kind(self) -> str:
        return self.kind

    def get_lineno(self) -> str:
        return self.lineno

    def set_type(self, exp_type:str):
        self.exp_type = exp_type


class Internal(Expression):
    def __init__(self, exp_type:str, name:str):
        super().__init__(0, "internal", exp_type)
        self.name = name
    
    def __repr__(self) -> str:
        return super().__repr__() + f"{self.name}\n"


class Feature:
    def __init__(self, feature_kind: str, feature_name:Identifier, feature_type:Identifier):
        self.feature_kind = feature_kind
        self.name_id = feature_name
        self.type_id = feature_type

    def __repr__(self) -> str:
        return self.feature_kind + "\n"

    def get_name(self) -> str:
        return self.name_id.get_name()

    def get_type(self) -> str:
        return self.type_id.get_name()

    def get_name_lineno(self) -> str:
        return self.name_id.get_lineno()
    
    def get_type_lineno(self) -> str:
        return self.type_id.get_lineno()



class Method(Feature):
    def __init__(self, feature_name:Identifier, feature_type:Identifier, 
                 formal_list:List[Formal], body:Expression, parent:str=None):
        super().__init__("method", feature_name, feature_type)
        self.formal_list = formal_list
        self.body = body
        self.parent = parent

    def __repr__(self) -> str:
        formal_repr = []
        for formal in self.formal_list:
            formal_repr.append(repr(formal))
        formal_str = "".join(formal_repr)

        return super().__repr__() + f"{repr(self.name_id)}{len(self.formal_list)}\n{formal_str}{repr(self.type_id)}{repr(self.body)}"

    def __eq__(self, __o: object) -> bool:
        return super().__eq__(__o)

    def get_formal_list(self) -> List[Formal]:
        return self.formal_list

    def set_parent(self, parent:str) -> None:
        self.parent = parent

    def get_parent(self) -> str:
        return self.parent

    def get_implementation_map_repr(self) -> str:
        formal_names = []
        for formal in self.formal_list:
            formal_names.append(formal.get_name() + "\n")

        return f"{self.get_name()}\n{len(self.formal_list)}\n{''.join(formal_names)}{self.parent}\n{repr(self.body)}"


class Attribute(Feature):
    def __init__(self, feature_name:Identifier, feature_type:Identifier, init:Expression):
        super().__init__("attribute_no_init" if init is None else "attribute_init", feature_name, feature_type)
        self.init = init

    def __repr__(self) -> str:
        initializer = self.init if self.init is not None else ""
        return super().__repr__() + f"{repr(self.name_id)}{repr(self.type_id)}{initializer}"

    def has_init(self):
        return self.init is not None

    def get_class_map_repr(self):
        if self.has_init():
            return f"initializer\n{self.get_name()}\n{self.get_type()}\n{repr(self.init)}"
        else:
            return f"no_initializer\n{self.get_name()}\n{self.get_type()}\n"


class Assign(Expression):
    def __init__(self, lineno:str, lhs:Identifier, rhs:Expression, exp_type:str=None):
        super().__init__(lineno, "assign", exp_type)
        self.lhs = lhs
        self.rhs = rhs
    
    def __repr__(self) -> str:
        return super().__repr__() + f"{repr(self.lhs)}{repr(self.rhs)}"


class Dispatch(Expression):
    def __init__(self, lineno:str, kind:str, method:Identifier, args:List[Expression],
            obj:Expression=None, class_type:Identifier=None, exp_type:str=None):
        super().__init__(lineno, kind, exp_type)
        self.obj = obj
        self.method = method
        self.args = args
        self.class_type = class_type

    def __repr__(self) -> str:
        args_repr = []
        for arg in self.args:
            args_repr.append(repr(arg))
        args_str = "".join(args_repr)

        class_type_str = repr(self.class_type) if self.class_type is not None else ""
        obj_str = repr(self.obj) if self.obj is not None else ""

        return super().__repr__() + f"{obj_str}{class_type_str}{repr(self.method)}{len(self.args)}\n{args_str}"

    def get_func_name(self) -> str:
        return self.method.get_name()


class DynamicDispatch(Dispatch):
    def __init__(self, lineno, obj:Expression, method:Identifier, args:List[Expression], exp_type:str=None):
        super().__init__(lineno, "dynamic_dispatch", method, args, obj, None, exp_type)


    def __repr__(self) -> str:
        return super().__repr__()


class StaticDispatch(Dispatch):
    def __init__(self, lineno:str, obj:Expression, class_type:Identifier, 
                 method:Identifier, args:List[Expression], exp_type:str=None):
        super().__init__(lineno, "static_dispatch", method, args, obj, class_type, exp_type)

    def __repr__(self) -> str:
        return super().__repr__()


class SelfDispatch(Dispatch):
    def __init__(self, lineno: str, method:Identifier, args:List[Expression], exp_type:str=None):
        super().__init__(lineno, "self_dispatch", method, args, None, None, exp_type)

    def __repr__(self) -> str:
        return super().__repr__()


class If(Expression):
    def __init__(self, lineno, condition:Expression, then_body:Expression, else_body:Expression, exp_type:str=None):
        super().__init__(lineno, "if", exp_type)
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def __repr__(self) -> str:
        return super().__repr__() + f"{repr(self.condition)}{repr(self.then_body)}{repr(self.else_body)}"


class While(Expression):
    def __init__(self, lineno:str, condition:Expression, while_body:Expression, exp_type:str=None):
        super().__init__(lineno, "while", exp_type)
        self.condition = condition
        self.while_body = while_body

    def __repr__(self) -> str:
        return super().__repr__() + f"{repr(self.condition)}{repr(self.while_body)}"

    
class Block(Expression):
    def __init__(self, lineno: str, body:List[Expression], exp_type:str=None):
        super().__init__(lineno, "block", exp_type)
        self.body = body

    def __repr__(self) -> str:
        body_repr = []
        for expr in self.body:
            body_repr.append(repr(expr))
        body_str = "".join(body_repr)
        return super().__repr__() + f"{len(self.body)}\n{body_str}"


class UnaryOp(Expression):
    def __init__(self, lineno:str, rhs:Expression, kind:str, exp_type:str=None):
        super().__init__(lineno, kind, exp_type)
        self.rhs:Expression = rhs

    def __repr__(self) -> str:
        return super().__repr__() + repr(self.rhs)


class IsVoid(UnaryOp):
    def __init__(self, lineno: str, rhs: Expression, exp_type:str=None):
        super().__init__(lineno, rhs, "isvoid", exp_type)

    def __repr__(self) -> str:
        return super().__repr__()


class Not(UnaryOp):
    def __init__(self, lineno: str, rhs: Expression, exp_type:str=None):
        super().__init__(lineno, rhs, "not", exp_type)
    
    def __repr__(self) -> str:
        return super().__repr__()


class Negate(UnaryOp):
    def __init__(self, lineno: str, rhs: Expression, exp_type:str=None):
        super().__init__(lineno, rhs, "negate", exp_type)

    def __repr__(self) -> str:
        return super().__repr__()


class Integer(Expression):
    def __init__(self, lineno:str, val:str, exp_type:str=None):
        super().__init__(lineno, "integer", exp_type)
        self.val = val
    
    def __repr__(self) -> str:
        return super().__repr__() + f"{self.val}\n"


class StringExp(Expression):
    def __init__(self, lineno:str, val:str, exp_type:str=None):
        super().__init__(lineno, "string", exp_type)
        self.val = val
    
    def __repr__(self) -> str:
        return super().__repr__() + f"{self.val}\n"


class New(Expression):
    def __init__(self, lineno:str, class_name:Identifier, exp_type:str=None):
        super().__init__(lineno, 'new', exp_type)
        self.class_name = class_name
    
    def __repr__(self) -> str:
        return super().__repr__() + repr(self.class_name)


class Binop(Expression):
    def __init__(self, lineno:str, lhs:str, rhs:str, kind:str, exp_type:str=None):
        super().__init__(lineno, kind, exp_type)
        self.lhs:Expression = lhs
        self.rhs:Expression = rhs
    
    def __repr__(self) -> str:
        return super().__repr__() + f"{repr(self.lhs)}{repr(self.rhs)}"


class Plus(Binop):
    def __init__(self, lineno:str, lhs:str, rhs:str, exp_type:str=None):
        super().__init__(lineno, lhs, rhs, 'plus', exp_type)
    
    def __repr__(self) -> str:
        return super().__repr__()


class Minus(Binop):
    def __init__(self, lineno:str, lhs:str, rhs:str, exp_type:str=None):
        super().__init__(lineno, lhs, rhs, 'minus', exp_type)

    def __repr__(self) -> str:
        return super().__repr__()


class Times(Binop):
    def __init__(self, lineno:str, lhs:str, rhs:str, exp_type:str=None):
        super().__init__(lineno, lhs, rhs, 'times', exp_type)
    
    def __repr__(self) -> str:
        return super().__repr__()


class Divide(Binop):
    def __init__(self, lineno:str, lhs:str, rhs:str, exp_type:str=None):
        super().__init__(lineno, lhs, rhs, 'divide', exp_type)
    
    def __repr__(self) -> str:
        return super().__repr__()


class Lt(Binop):
    def __init__(self, lineno:str, lhs:str, rhs:str, exp_type:str=None):
        super().__init__(lineno, lhs, rhs, 'lt', exp_type)

    def __repr__(self) -> str:
        return super().__repr__()


class Le(Binop):
    def __init__(self, lineno:str, lhs:str, rhs:str, exp_type:str=None):
        super().__init__(lineno, lhs, rhs, 'le', exp_type)

    def __repr__(self) -> str:
        return super().__repr__()


class Eq(Binop):
    def __init__(self, lineno:str, lhs:str, rhs:str, exp_type:str=None):
        super().__init__(lineno, lhs, rhs, 'eq', exp_type)

    def __repr__(self) -> str:
        return super().__repr__()


class Bool(Expression):
    def __init__(self, lineno: str, val:str, exp_type:str=None):
        super().__init__(lineno, val, exp_type)

    def __repr__(self) -> str:
        return super().__repr__()


class Variable(Expression):
    def __init__(self, lineno: str, var:Identifier, exp_type:str=None):
        super().__init__(lineno, "identifier", exp_type)
        self.var = var

    def __repr__(self) -> str:
        return super().__repr__() + repr(self.var)


class LetBinding:
    def __init__(self, var:Identifier, var_type:Identifier, val:Expression = None):
        self.var = var
        self.var_type = var_type
        self.val = val

    def __repr__(self) -> str:
        let_init = "let_binding_init\n" if self.has_init() else "let_binding_no_init\n"
        let_expr = repr(self.val) if self.val is not None else ""
        return f"{let_init}{repr(self.var)}{repr(self.var_type)}{let_expr}"

    def has_init(self) -> bool:
        return self.val is not None

    def get_var_name(self) -> str:
        return self.var.get_name()


class Let(Expression):
    def __init__(self, lineno: str, binding_list:List[LetBinding], expr:Expression, exp_type:str=None):
        super().__init__(lineno, "let", exp_type)
        self.binding_list = binding_list
        self.expr = expr

    def __repr__(self) -> str:
        binding_repr = []
        for binding in self.binding_list:
            binding_repr.append(repr(binding))
        binding_str = "".join(binding_repr)
        return super().__repr__() + f"{len(self.binding_list)}\n{binding_str}{repr(self.expr)}"


class CaseElement:
    def __init__(self, formal:Formal, expr:Expression):
        self.formal = formal
        self.expr = expr

    def __repr__(self) -> str:
        return f"{repr(self.formal)}{repr(self.expr)}"
    
    def get_name(self) -> str:
        return self.formal.get_name()

    def get_type(self) -> str:
        return self.formal.get_type()
    
    def get_name_lineno(self) -> str:
        return self.formal.get_name_lineno()
    
    def get_type_lineno(self) -> str:
        return self.formal.get_type_lineno()


class Case(Expression):
    def __init__(self, lineno: str, case_expr:Expression, case_list:List[CaseElement], exp_type:str=None):
        super().__init__(lineno, "case", exp_type)
        self.case_expr = case_expr
        self.case_list = case_list

    def __repr__(self) -> str:
        case_repr = []
        for case in self.case_list:
            case_repr.append(repr(case))
        case_str = "".join(case_repr)

        return super().__repr__() + f"{repr(self.case_expr)}{len(self.case_list)}\n{case_str}"


class Class:
    def __init__(self, class_name:Identifier, pred:Identifier, feature_list:List[Feature]):
        self.class_id = class_name
        self.pred_id = pred
        self.feature_list = feature_list

    def __repr__(self) -> str:
        if self.pred_id is None:
            pred = "no_inherits\n"
        else:
            pred = f"inherits\n{repr(self.pred_id)}"

        feature_repr = []
        for feature in self.feature_list:
            feature_repr.append(repr(feature))
        feature_str = "".join(feature_repr)

        return f"{repr(self.class_id)}{pred}{len(self.feature_list)}\n{feature_str}"
    
    def get_class_id(self):
        return self.class_id
    
    def get_class_name(self):
        return self.class_id.get_name()
    
    def get_class_lineno(self):
        return self.class_id.get_lineno()
    
    def get_pred_id(self):
        return self.pred_id
    
    def get_pred_name(self):
        return self.pred_id.get_name() if self.pred_id is not None else "Object"

    def get_pred_lineno(self):
        return self.pred_id.get_lineno()
    
    def get_feature_list(self):
        return self.feature_list


class ClassAttribute:
    def __init__(self, attr_name:str, attr_kind:str, attr_type:str, attr_expr:Expression=None):
        self.attr_name = attr_name
        self.attr_kind = attr_kind
        self.attr_type = attr_type
        self.attr_expr = attr_expr

    def __repr__(self) -> str:
        expr_str = "" if self.attr_expr is None else repr(self.attr_expr)
        return f"{self.attr_kind}\n{self.attr_name}\n{self.attr_type}\n{expr_str}"
    
    def get_name(self) -> str:
        return self.attr_name

    def get_type(self) -> str:
        return self.attr_type


class ImplMethod:
    def __init__(self, method_name:str, formal_list:List[str], parent:str, expr:Expression=None):
        self.method_name = method_name
        self.formal_list = formal_list
        self.parent = parent
        self.expr = expr
    
    def __repr__(self) -> str:
        formal_repr = []
        for formal in self.formal_list:
            formal_repr.append(formal + "\n")
        formal_str = "".join(formal_repr)
        expr_str = "" if self.expr is None else repr(self.expr)

        return f"{self.method_name}\n{len(self.formal_list)}\n{formal_str}{self.parent}\n{expr_str}"

    def get_name(self) -> str:
        return self.method_name

    def get_formal_list(self) -> List[str]:
        return self.formal_list


class ClassMapEntry:
    def __init__(self, class_name:str, attr_list:List[ClassAttribute]):
        self.class_name = class_name
        self.attr_list = attr_list

    def __repr__(self) -> str:
        attr_repr = []
        for attr in self.attr_list:
            attr_repr.append(repr(attr))
        attr_str = "".join(attr_repr)

        return f"{self.class_name}\n{len(self.attr_list)}\n{attr_str}"


class ImplMapEntry:
    def __init__(self, class_name:str, method_list:List[ImplMethod]):
        self.class_name = class_name
        self.method_list = method_list
    
    def __repr__(self) -> str:
        method_repr = []
        for method in self.method_list:
            method_repr.append(repr(method))
        method_str = "".join(method_repr)

        return f"{self.class_name}\n{len(self.method_list)}\n{method_str}"


class ParentMapEntry:
    def __init__(self, parent:str, child:str):
        self.parent = parent
        self.child = child

    def __repr__(self) -> str:
        return f"{self.child}\n{self.parent}\n"