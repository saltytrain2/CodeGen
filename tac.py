from __future__ import annotations
from typing import List, Tuple
from collections import defaultdict
from tacnodes import *

class DeclarationList(object):
    def __init__(self):
        self.obj_list:List[Tuple[Any, TacReg]] = []
    
    def add_node(self, ast_node:Any, tacreg:TacReg) -> None:
        self.obj_list.append((ast_node, tacreg))

    def get_tacreg(self, ast_node:Any) -> TacReg:
        for item, tacreg in self.obj_list:
            if ast_node is item:
                return tacreg

        raise TypeError("You looked for something nonexistent in the declaration list")

    def clear(self) -> None:
        self.obj_list.clear()

class MethodOffsetMap(object):
        def __init__(self):
            self.method_map:Dict[str, Dict[str, int]] = defaultdict(dict)

        def add_method(self, class_name:str, method_name:str, offset:int) -> None:
            self.method_map[class_name][method_name] = offset
        
        def get_method_offset(self, class_name:str, method_name:str) -> int:
            return self.method_map[class_name][method_name]
        

class Tac(object):
    class_map:Dict[str, List[ClassAttribute]] = defaultdict(list)
    impl_map:Dict[str, List[ImplMethod]] = defaultdict(list)
    parent_map:Dict[str, str] = defaultdict(str)
    symbol_table:Dict[str, List[TacReg]] = defaultdict(list)
    class_tags:Dict[str, int] = defaultdict(int, {"Bool":0, "Int":1, "String":2, "Object":3, "IO":4})
    attr_table:Dict[str, int] = defaultdict(int)
    method_offsets:MethodOffsetMap = MethodOffsetMap()
    cur_class = ""

    def __init__(self, class_map:List[ClassMapEntry], impl_map:List[ImplMapEntry],
            parent_map:List[ParentMapEntry]):
        count = 5
        for entry in class_map:
            self.class_map[entry.class_name] = entry.attr_list
            if entry.class_name not in self.class_tags.keys():
                self.class_tags[entry.class_name] = count
                count += 1
        
        for entry in impl_map:
            self.impl_map[entry.class_name] = entry.method_list
            for i, method in enumerate(self.impl_map[entry.class_name]):
                self.method_offsets.add_method(entry.class_name, method.method_name, 16 + 8 * i)

        for entry in parent_map:
            self.parent_map[entry.child] = entry.parent

        self.declaration_list = DeclarationList()
        self.processed_funcs:List[TacFunc] = []
        self.cur_tacfunc = None
        self.num = 0

    def self_reg(self) -> TacReg:
        return self.symbol_table["self"][-1]

    def tacgen(self) -> None:
        for c in self.impl_map:
            if c in {"Object", "Bool", "String", "Int", "IO"}:
                continue

            self.cur_class = c
            offset = 3
            for attr in self.class_map[c]:
                self.attr_table[attr.get_name()] = offset
                offset += 1

            self.declaration_list.clear()
            self.tacgen_constructor(c)
            for method in self.impl_map[c]:
                if method.parent != c:
                    continue
                self.tacgen_func(method)
            
            self.attr_table.clear()

    def tacgen_constructor(self, c:str):
        self.cur_tacfunc = TacFunc(f"{c}..new")
        num_elems = 3 + len(self.class_map[c])
        size = 8
        for attr in self.class_map[c]:
            if attr.attr_expr is not None:
                self.create_stack_vars(attr.attr_expr)
        calloc_elems_reg = self.cur_tacfunc.create_reg()
        calloc_size_reg = self.cur_tacfunc.create_reg()
        temp_reg = self.cur_tacfunc.create_reg()
        self_reg = self.cur_tacfunc.create_reg()
        self.cur_tacfunc.append(TacLoadImm(TacImm(num_elems), calloc_elems_reg))
        self.cur_tacfunc.append(TacLoadImm(TacImm(size), calloc_size_reg))
        self.cur_tacfunc.append(TacSyscall("calloc@PLT", [calloc_elems_reg, calloc_size_reg], temp_reg))
        self.cur_tacfunc.append(TacMarkSelf(temp_reg, self_reg))
        self.cur_tacfunc.set_self_reg(self_reg)
        self.symbol_table["self"].append(self_reg)

        # store class_tag, obj_size, and vtable
        class_tag_reg = self.cur_tacfunc.create_reg()
        self.cur_tacfunc.append(TacLoadImm(TacImm(self.class_tags[c]), class_tag_reg))
        self.cur_tacfunc.append(TacStoreSelf(class_tag_reg, self_reg, 0))
        size_reg = self.cur_tacfunc.create_reg()
        self.cur_tacfunc.append(TacLoadImm(TacImm(num_elems), size_reg))
        self.cur_tacfunc.append(TacStoreSelf(size_reg, self_reg, 1))
        vtable_reg = self.cur_tacfunc.create_reg()
        self.cur_tacfunc.append(TacLoadImm(TacImmLabel(f"{c}..vtable"), vtable_reg))
        self.cur_tacfunc.append(TacStoreSelf(vtable_reg, self_reg, 2))

        for attr in self.class_map[c]:
            if attr.attr_type in {"Bool", "Int", "String"}:
                temp_reg = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacCreate(attr.attr_type, temp_reg))
                self.cur_tacfunc.append(TacStoreSelf(temp_reg, self_reg, self.attr_table[attr.get_name()]))
                
        for attr in self.class_map[c]:
            if attr.attr_kind == "initializer":
                attr_ret = self.tacgen_exp(attr.attr_expr)
                self.cur_tacfunc.append(TacStoreSelf(attr_ret, self_reg, self.attr_table[attr.get_name()]))
        
        self.cur_tacfunc.append(TacRet(self_reg))
        self.symbol_table["self"].pop()
        self.processed_funcs.append(self.cur_tacfunc)
        self.declaration_list.clear()

    def tacgen_func(self, method:ImplMethod) -> None:
        self.cur_tacfunc = TacFunc(f"{method.parent}.{method.get_name()}")

        self_param = self.cur_tacfunc.create_reg()
        params:List[TacReg] = []
        param_names:List[str] = []
        for param in method.get_formal_list():
            params.append(self.cur_tacfunc.create_reg())
            param_names.append(param)

        self.cur_tacfunc.set_params([self_param] + params)
        self.create_stack_vars(method.expr)

        local_regs = [self.cur_tacfunc.create_reg(True) for _ in params]
        for i, param in enumerate(params):
            name = param_names[i]
            self.cur_tacfunc.append(TacAlloc(name, local_regs[i]))
            self.symbol_table[name].append(local_regs[i])

        self_obj = self.cur_tacfunc.create_reg()
        self.cur_tacfunc.append(TacMarkSelf(self_param, self_obj))
        self.cur_tacfunc.set_self_reg(self_obj)
        self.symbol_table["self"].append(self_obj)

        for i, param in enumerate(params):
            self.cur_tacfunc.append(TacStore(param, local_regs[i]))

        ret_reg = self.tacgen_exp(method.expr)
        self.cur_tacfunc.append(TacRet(ret_reg))
        self.processed_funcs.append(self.cur_tacfunc)

        for param_name in param_names:
            self.symbol_table[param_name].pop()
        self.symbol_table["self"].pop()

        self.declaration_list.clear()

    def create_let_stack_vars(self, binding:LetBinding):
        self.declaration_list.add_node(binding, self.cur_tacfunc.create_reg(True))
        self.cur_tacfunc.append(TacAlloc(binding.var_type.name, self.declaration_list.get_tacreg(binding)))
        self.create_stack_vars(binding.val)

    def create_case_stack_vars(self, case_elem:CaseElement):
        self.declaration_list.add_node(case_elem, self.cur_tacfunc.create_reg(True))
        self.cur_tacfunc.append(TacAlloc(case_elem.get_type(), self.declaration_list.get_tacreg(case_elem)))
        self.create_stack_vars(case_elem.expr)

    def gen_case_labels(self, case_list:List[CaseElement], error_label:TacReg) -> List[TacLabel]:
        def visit(self:Tac, class_name:str, case_labels:List[TacLabel]) -> TacLabel:
            index = self.class_tags[class_name]
            if case_labels[index] is not None:
                return case_labels[index]

            parent_class = self.parent_map[class_name]
            case_labels[index] = visit(self, parent_class, case_labels)
            return case_labels[index]

        # generate assume every label jumps to the error condition
        case_labels = [None for _ in self.class_tags]

        for case_elem in case_list:
            case_labels[self.class_tags[case_elem.get_type()]] = self.cur_tacfunc.create_label()

        # make our base case condition: if Object has not been assigned a label it has to fall through
        if case_labels[self.class_tags["Object"]] is None:
            case_labels[self.class_tags["Object"]] = error_label

        for class_name, class_tag in self.class_tags.items():
            # walk through the parent map, when we find the first non-error label we are good
            case_labels[class_tag] = visit(self, class_name, case_labels)
        
        return case_labels

    def add_tac_create(self, obj_type:str) -> TacReg:
        create_reg = self.cur_tacfunc.create_reg()
        create_inst = TacCreate(obj_type, create_reg) if obj_type != "SELF_TYPE" else TacCreate(obj_type, create_reg, self.self_reg())
        self.cur_tacfunc.append(create_inst)
        return create_reg

    def create_stack_vars(self, exp:Expression) -> None:
        # search for any variables that we should put on the stack, primarily let variables and case variables
        if exp is None:
            return

        if isinstance(exp, Binop):
            self.create_stack_vars(exp.lhs)
            self.create_stack_vars(exp.rhs)
        elif isinstance(exp, UnaryOp):
            self.create_stack_vars(exp.rhs)
        elif isinstance(exp, Block):
            for expr in exp.body:
                self.create_stack_vars(expr)
        elif isinstance(exp, If):
            self.create_stack_vars(exp.condition)
            self.create_stack_vars(exp.then_body)
            self.create_stack_vars(exp.else_body)
        elif isinstance(exp, While):
            self.create_stack_vars(exp.condition)
            self.create_stack_vars(exp.while_body)
        elif isinstance(exp, Let):
            for binding in exp.binding_list:
                self.create_let_stack_vars(binding)
            self.create_stack_vars(exp.expr)
        elif isinstance(exp, Case):
            self.create_stack_vars(exp.case_expr)
            for case_elem in exp.case_list:
                self.create_case_stack_vars(case_elem)
        elif isinstance(exp, Dispatch):
            self.create_stack_vars(exp.obj)
            for arg in exp.args:
                self.create_stack_vars(arg)
        elif isinstance(exp, Assign):
            self.create_stack_vars(exp.rhs)
        
        if isinstance(exp, (Case, If)):
            self.declaration_list.add_node(exp, self.cur_tacfunc.create_reg(True))
            self.cur_tacfunc.append(TacAlloc(exp.exp_type, self.declaration_list.get_tacreg(exp)))

    def tacgen_exp(self, exp:Expression) -> TacReg:
        if isinstance(exp, Binop):
            lhs_reg = self.tacgen_exp(exp.lhs)
            rhs_reg = self.tacgen_exp(exp.rhs)
            #rhs_reg = self.tacgen_exp(exp.rhs)
            if isinstance(exp, (Plus, Minus, Times, Divide)):
                lhs_prim = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacLoadPrim(lhs_reg, lhs_prim))
                rhs_prim = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacLoadPrim(rhs_reg, rhs_prim))
                res_reg = self.cur_tacfunc.create_reg()
                if isinstance(exp, Plus):
                    self.cur_tacfunc.append(TacAdd(lhs_prim, rhs_prim, res_reg))
                elif isinstance(exp, Minus):
                    self.cur_tacfunc.append(TacSub(lhs_prim, rhs_prim, res_reg))
                elif isinstance(exp, Times):
                    self.cur_tacfunc.append(TacMul(lhs_prim, rhs_prim, res_reg))
                elif isinstance(exp, Divide):
                    zero_reg = self.cur_tacfunc.create_reg()
                    self.cur_tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
                    self.cur_tacfunc.append(TacCmp(zero_reg, rhs_prim))
                    true_label = self.cur_tacfunc.create_label()
                    false_label = self.cur_tacfunc.create_label()
                    self.cur_tacfunc.append(TacBr(TacCmpOp.NE, false_label, true_label))
                    self.cur_tacfunc.append(true_label)
                    error_str = self.cur_tacfunc.create_reg()
                    self.cur_tacfunc.append(TacLoadImm(TacStr(f"ERROR: {exp.lineno}: Exception: division by zero\\n"), error_str))
                    self.cur_tacfunc.append(TacExit(error_str))
                    self.cur_tacfunc.append(TacUnreachable())
                    self.cur_tacfunc.append(false_label)
                    self.cur_tacfunc.append(TacDiv(lhs_prim, rhs_prim, res_reg))
                create_reg = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacCreate("Int", create_reg))
                self.cur_tacfunc.append(TacStorePrim(res_reg, create_reg))
                return create_reg
            else:
                res_reg = self.cur_tacfunc.create_reg()
                if isinstance(exp, Lt):
                    self.cur_tacfunc.append(TacSyscall("lt_helper", [lhs_reg, rhs_reg], res_reg))
                elif isinstance(exp, Le):
                    self.cur_tacfunc.append(TacSyscall("le_helper", [lhs_reg, rhs_reg], res_reg))
                else:
                    self.cur_tacfunc.append(TacSyscall("eq_helper", [lhs_reg, rhs_reg], res_reg))
                return res_reg

        elif isinstance(exp, Integer):
            int_reg = self.cur_tacfunc.create_reg()
            prim_int_val = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoadImm(TacImm(int(exp.val)), prim_int_val))
            self.cur_tacfunc.append(TacCreate("Int", int_reg))
            self.cur_tacfunc.append(TacStorePrim(prim_int_val, int_reg))
            return int_reg
        elif isinstance(exp, StringExp):
            str_reg = self.cur_tacfunc.create_reg()
            prim_str_val = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoadImm(TacStr(exp.val), prim_str_val))
            self.cur_tacfunc.append(TacCreate("String", str_reg))
            self.cur_tacfunc.append(TacStorePrim(prim_str_val, str_reg))
            return str_reg
        elif isinstance(exp, Bool):
            bool_reg = self.cur_tacfunc.create_reg()
            prim_bool_val = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoadImm(TacImm(1 if exp.kind == "true" else 0), prim_bool_val))
            self.cur_tacfunc.append(TacCreate("Bool", bool_reg))
            self.cur_tacfunc.append(TacStorePrim(prim_bool_val, bool_reg))
            return bool_reg
        elif isinstance(exp, Dispatch):
            obj_reg = self.tacgen_exp(exp.obj) if exp.obj is not None else self.self_reg()
            if not isinstance(exp, SelfDispatch):
                void_branch = self.cur_tacfunc.create_label()
                nonvoid_branch = self.cur_tacfunc.create_label()
                void_reg = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacLoadImm(TacImm(0), void_reg))
                self.cur_tacfunc.append(TacCmp(void_reg, obj_reg))
                self.cur_tacfunc.append(TacBr(TacCmpOp.NE, nonvoid_branch, void_branch))
                self.cur_tacfunc.append(void_branch)
                error_str = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacLoadImm(TacStr(f"ERROR: {exp.lineno}: Exception: dispatch on void\\n"), error_str))
                self.cur_tacfunc.append(TacExit(error_str))
                self.cur_tacfunc.append(TacUnreachable())
                self.cur_tacfunc.append(nonvoid_branch)

            param_regs = [obj_reg]
            for arg in exp.args:
                param_regs.append(self.tacgen_exp(arg))
            
            ret_reg = self.cur_tacfunc.create_reg()
            func_str = f"{exp.class_type.name}.{exp.get_func_name()}" if isinstance(exp, StaticDispatch) else f"{exp.get_func_name()}"
            if isinstance(exp, StaticDispatch):
                class_name = exp.class_type.name
            elif isinstance(exp, SelfDispatch) or exp.obj.exp_type == "SELF_TYPE":
                class_name = self.cur_class
            else:
                class_name = exp.obj.exp_type
            
            offset = self.method_offsets.get_method_offset(class_name, exp.get_func_name())
            self.cur_tacfunc.append(TacCall(func_str, param_regs, ret_reg, offset))
            return ret_reg
        elif isinstance(exp, Variable):
            var_name = exp.var.name
            temp_reg = self.cur_tacfunc.create_reg()
            if self.symbol_table[var_name]:
                self.cur_tacfunc.append(TacLoad(self.symbol_table[var_name][-1], temp_reg))
            else:
                self.cur_tacfunc.append(TacLoad(self.symbol_table["self"][-1], temp_reg, self.attr_table[var_name]))
            return temp_reg
        elif isinstance(exp, New):
            dest_reg = self.add_tac_create(exp.class_name.get_name())
            return dest_reg
        elif isinstance(exp, UnaryOp):
            rhs_reg = self.tacgen_exp(exp.rhs)
            dest_reg = self.cur_tacfunc.create_reg()
            if isinstance(exp, Negate):
                int_prim = self.cur_tacfunc.create_reg()
                negative_reg = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacLoadPrim(rhs_reg, int_prim))
                self.cur_tacfunc.append(TacNegate(int_prim, negative_reg))
                self.cur_tacfunc.append(TacCreate("Int", dest_reg))
                self.cur_tacfunc.append(TacStorePrim(negative_reg, dest_reg))
            elif isinstance(exp, Not):
                bool_prim = self.cur_tacfunc.create_reg()
                logical_negate_reg = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacLoadPrim(rhs_reg, bool_prim))
                self.cur_tacfunc.append(TacNot(bool_prim, logical_negate_reg))
                self.cur_tacfunc.append(TacCreate("Bool", dest_reg))
                self.cur_tacfunc.append(TacStorePrim(logical_negate_reg, dest_reg))
            else:
                # isvoid
                is_zero_reg = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacIsZero(rhs_reg, is_zero_reg))
                self.cur_tacfunc.append(TacCreate("Bool", dest_reg))
                self.cur_tacfunc.append(TacStorePrim(is_zero_reg, dest_reg))
            return dest_reg
        elif isinstance(exp, If):
            true_label = self.cur_tacfunc.create_label()
            false_label = self.cur_tacfunc.create_label()
            end_label = self.cur_tacfunc.create_label()
            cond_reg = self.tacgen_exp(exp.condition)
            boolean_reg = self.cur_tacfunc.create_reg()
            false_reg = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoad(cond_reg, boolean_reg, 3))
            self.cur_tacfunc.append(TacLoadImm(TacImm(0), false_reg))
            self.cur_tacfunc.append(TacCmp(boolean_reg, false_reg))
            self.cur_tacfunc.append(TacBr(TacCmpOp.NE, true_label, false_label))

            self.cur_tacfunc.append(true_label)
            then_reg = self.tacgen_exp(exp.then_body)
            self.cur_tacfunc.append(TacStore(then_reg, self.declaration_list.get_tacreg(exp)))
            self.cur_tacfunc.append(TacBr(true_label=end_label))

            self.cur_tacfunc.append(false_label)
            else_reg = self.tacgen_exp(exp.else_body)
            self.cur_tacfunc.append(TacStore(else_reg, self.declaration_list.get_tacreg(exp)))
            self.cur_tacfunc.append(TacBr(true_label=end_label))
            self.cur_tacfunc.append(end_label)

            ret_reg = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoad(self.declaration_list.get_tacreg(exp), ret_reg))
            return ret_reg
        elif isinstance(exp, While):
            while_start = self.cur_tacfunc.create_label()
            while_body = self.cur_tacfunc.create_label()
            while_end = self.cur_tacfunc.create_label()
            self.cur_tacfunc.append(TacBr(true_label=while_start))
            self.cur_tacfunc.append(while_start)
            cond_reg = self.tacgen_exp(exp.condition)
            boolean_reg = self.cur_tacfunc.create_reg()
            false_reg = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoadPrim(cond_reg, boolean_reg))
            self.cur_tacfunc.append(TacLoadImm(TacImm(0), false_reg))
            self.cur_tacfunc.append(TacCmp(boolean_reg, false_reg))
            self.cur_tacfunc.append(TacBr(TacCmpOp.NE, while_body, while_end))

            self.cur_tacfunc.append(while_body)
            self.tacgen_exp(exp.while_body)
            self.cur_tacfunc.append(TacBr(true_label=while_start))

            self.cur_tacfunc.append(while_end)
            void_reg = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoadImm(TacImm(0), void_reg))
            return void_reg
        elif isinstance(exp, Block):
            for expr in exp.body:
                ret_reg = self.tacgen_exp(expr)
            return ret_reg
        elif isinstance(exp, Assign):
            rhs_reg = self.tacgen_exp(exp.rhs)
            ret_reg = self.cur_tacfunc.create_reg()

            # we differentiate between a normal variable and a class attribute
            if self.symbol_table[exp.lhs.name]:
                self.cur_tacfunc.append(TacStore(rhs_reg, self.symbol_table[exp.lhs.name][-1]))
                self.cur_tacfunc.append(TacLoad(self.symbol_table[exp.lhs.name][-1], ret_reg))
            else:
                self.cur_tacfunc.append(TacStoreSelf(rhs_reg, self.self_reg(), self.attr_table[exp.lhs.name]))
                self.cur_tacfunc.append(TacLoad(self.self_reg(), ret_reg, self.attr_table[exp.lhs.name]))
            return ret_reg
        elif isinstance(exp, Let):
            # adding additional registers into the symbol table
            for let_binding in exp.binding_list:
                binding_name = let_binding.get_var_name()
                if let_binding.var_type.get_name() in {"Bool", "Int", "String"}:
                    create_reg = self.cur_tacfunc.create_reg()
                    self.cur_tacfunc.append(TacCreate(let_binding.var_type.get_name(), create_reg))
                    self.cur_tacfunc.append(TacStore(create_reg, self.declaration_list.get_tacreg(let_binding)))
                else:
                    void_reg = self.cur_tacfunc.create_reg()
                    self.cur_tacfunc.append(TacLoadImm(TacImm(0), void_reg))
                    self.cur_tacfunc.append(TacStore(void_reg, self.declaration_list.get_tacreg(let_binding)))
                if let_binding.has_init():
                    init_res = self.tacgen_exp(let_binding.val)
                    self.cur_tacfunc.append(TacStore(init_res, self.declaration_list.get_tacreg(let_binding)))
                self.symbol_table[binding_name].append(self.declaration_list.get_tacreg(let_binding))
            
            ret_reg = self.tacgen_exp(exp.expr)

            for let_binding in exp.binding_list:
                self.symbol_table[let_binding.get_var_name()].pop()
            
            return ret_reg

        elif isinstance(exp, Case):
            # set up the branches
            cur_obj = self.tacgen_exp(exp.case_expr)
            void_branch = self.cur_tacfunc.create_label()
            nonvoid_branch = self.cur_tacfunc.create_label()
            void_reg = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoadImm(TacImm(0), void_reg))
            self.cur_tacfunc.append(TacCmp(void_reg, cur_obj))
            self.cur_tacfunc.append(TacBr(TacCmpOp.NE, nonvoid_branch, void_branch))
            self.cur_tacfunc.append(void_branch)
            error_str = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoadImm(TacStr(f"ERROR: {exp.lineno}: Exception: case on void\\n"), error_str))
            self.cur_tacfunc.append(TacExit(error_str))
            self.cur_tacfunc.append(TacUnreachable())
            self.cur_tacfunc.append(nonvoid_branch)

            # load in the classtag
            class_tag = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoad(cur_obj, class_tag, 0))

            # generate all the labels
            error_label = self.cur_tacfunc.create_label()
            case_labels = self.gen_case_labels(exp.case_list, error_label)
            
            # do comparison with classtags
            for i, true_label in enumerate(case_labels):
                false_label = self.cur_tacfunc.create_label() if i != len(case_labels) - 1 else error_label
                case_class_tag = self.cur_tacfunc.create_reg()
                self.cur_tacfunc.append(TacLoadImm(TacImm(i), case_class_tag))
                self.cur_tacfunc.append(TacCmp(case_class_tag, class_tag))
                self.cur_tacfunc.append(TacBr(TacCmpOp.EQ, true_label, false_label))
                self.cur_tacfunc.append(false_label)

            # if we fell through, we now need to generate an error condition
            error_str = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoadImm(TacStr(f"ERROR: {exp.lineno}: Exception: case without matching branch\\n"), error_str))
            self.cur_tacfunc.append(TacExit(error_str))
            self.cur_tacfunc.append(TacUnreachable())

            # now generate the case expression labels
            case_end = self.cur_tacfunc.create_label()
            for case_elem in exp.case_list:
                self.cur_tacfunc.append(case_labels[self.class_tags[case_elem.get_type()]])
                self.symbol_table[case_elem.get_name()].append(self.declaration_list.get_tacreg(case_elem))
                self.cur_tacfunc.append(TacStore(cur_obj, self.declaration_list.get_tacreg(case_elem)))
                elem_reg = self.tacgen_exp(case_elem.expr)
                self.symbol_table[case_elem.get_name()].pop()
                self.cur_tacfunc.append(TacStore(elem_reg, self.declaration_list.get_tacreg(exp)))
                self.cur_tacfunc.append(TacBr(true_label=case_end))

            self.cur_tacfunc.append(case_end)
            ret_reg = self.cur_tacfunc.create_reg()
            self.cur_tacfunc.append(TacLoad(self.declaration_list.get_tacreg(exp), ret_reg))
            return ret_reg

    def debug_tac(self) -> None:
        for func in self.processed_funcs:
            print(repr(func))

    def get_tacfuncs(self) -> List[TacFunc]:
        return self.processed_funcs
