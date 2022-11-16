from __future__ import annotations
from typing import List, Tuple
from tacnodes import *
from coolbase import BASE_CLASS_METHODS


class Tac(object):
    class_map:Dict[str, List[ClassAttribute]] = defaultdict(list)
    impl_map:Dict[str, List[ImplMethod]] = defaultdict(list)
    parent_map:Dict[str, str] = defaultdict(str)
    symbol_table:Dict[str, List[TacReg]] = defaultdict(list)
    class_tags:Dict[str, int] = defaultdict(int)
    attr_table:Dict[str, int] = defaultdict(int)

    def __init__(self, class_map:List[ClassMapEntry], impl_map:List[ImplMapEntry],
            parent_map:List[ParentMapEntry]):
        count = 0
        for entry in class_map:
            self.class_map[entry.class_name] = entry.attr_list
            self.class_tags[entry.class_name] = count
            count += 1
        
        for entry in impl_map:
            self.impl_map[entry.class_name] = entry.method_list

        for entry in parent_map:
            self.parent_map[entry.child] = entry.parent

        self.declaration_map:Dict[Expression, TacReg] = defaultdict(TacReg, num=-1)
        self.processed_funcs:List[TacFunc] = []
        self.cur_tacfunc = None
        self.num = 0

    def self_reg(self) -> TacReg:
        return self.symbol_table["self"][-1]

    def tacgen(self) -> None:
        for c in self.impl_map:
            if c in {"Object", "Bool", "String", "Int", "IO"}:
                self.processed_funcs.extend(BASE_CLASS_METHODS[c])
                continue

            offset = 3
            for attr in self.class_map[c]:
                self.attr_table[attr.get_name()] = offset
                offset += 1

            self.tacgen_constructor(c)
            for method in self.impl_map[c]:
                if method.parent != c:
                    continue
                self.tacgen_func(method)
            
            self.attr_table.clear()

    def create_reg(self, isstack:bool=False) -> TacReg:
        temp = TacReg(self.num, isstack)
        self.num += 1
        return temp
    
    def create_label(self) -> TacLabel:
        temp = TacLabel(self.num)
        self.num += 1
        return temp

    def tacgen_constructor(self, c:str):
        temp_num = self.num
        self.cur_tacfunc = TacFunc(f"{c}..new", None)
        obj_reg = self.create_reg(True)
        size = 8 * len(self.class_map[c]) + 24
        self.cur_tacfunc.append(TacAlloc(c, obj_reg))
        malloc_size_reg = self.create_reg()
        temp_reg = self.create_reg()
        self.cur_tacfunc.append(TacLoadImm(TacImm(size), malloc_size_reg))
        self.cur_tacfunc.append(TacSyscall("malloc", [malloc_size_reg], temp_reg))
        self.cur_tacfunc.append(TacStore(temp_reg, obj_reg))

        # store class_tag, obj_size, and vtable
        class_tag_reg = self.create_reg()
        self.cur_tacfunc.append(TacLoadImm(TacImm(self.class_tags[c]), class_tag_reg))
        self.cur_tacfunc.append(TacStore(class_tag_reg, obj_reg, 0))
        size_reg = self.create_reg()
        self.cur_tacfunc.append(TacLoadImm(TacImm(size), size_reg))
        self.cur_tacfunc.append(TacStore(size_reg, obj_reg, 1))
        vtable_reg = self.create_reg()
        self.cur_tacfunc.append(TacLoadImm(TacImmLabel(f"{c}..vtable"), vtable_reg))
        self.cur_tacfunc.append(TacStore(vtable_reg, obj_reg, 2))

        for attr in self.class_map[c]:
            if attr.attr_type in {"Bool", "Int", "String"}:
                temp_reg = self.create_reg()
                self.cur_tacfunc.append(TacCreate(attr.attr_type, temp_reg))
                self.cur_tacfunc.append(TacStore(temp_reg, obj_reg, self.attr_table[attr.get_name()]))
            else:
                zero_reg = self.create_reg()
                self.cur_tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
                self.cur_tacfunc.append(TacStore(zero_reg, obj_reg, self.attr_table[attr.get_name()]))
        
        ret_reg = self.create_reg()
        self.cur_tacfunc.append(TacLoad(obj_reg, ret_reg))
        self.cur_tacfunc.append(TacRet(ret_reg))

        self.processed_funcs.append(self.cur_tacfunc)
        self.num = temp_num
        self.declaration_map.clear()

    def tacgen_func(self, method:ImplMethod) -> None:
        temp_num = self.num

        params:List[TacReg] = [self.create_reg()]
        param_names:List[str] = ["self"]
        for param in method.get_formal_list():
            params.append(self.create_reg())
            param_names.append(param)

        self.cur_tacfunc = TacFunc(f"{method.parent}.{method.get_name()}", params)
        self.create_stack_vars(method.expr)

        local_regs = [self.create_reg(True) for _ in params]
        for i, param in enumerate(params):
            name = param_names[i]
            self.cur_tacfunc.append(TacAlloc(name, local_regs[i]))
            self.symbol_table[name].append(local_regs[i])

        for i, param in enumerate(params):
            self.cur_tacfunc.append(TacStore(param, local_regs[i]))

        ret_reg = self.tacgen_exp(method.expr)
        self.cur_tacfunc.append(TacRet(ret_reg))
        self.processed_funcs.append(self.cur_tacfunc)

        for param_name in param_names:
            self.symbol_table[param_name].pop()

        self.num = temp_num
        self.declaration_map.clear()

    def create_let_stack_vars(self, binding:LetBinding):
        self.declaration_map[binding] = self.create_reg(True)
        self.cur_tacfunc.append(TacAlloc(binding.var_type.name, self.declaration_map[binding]))
        self.create_stack_vars(binding.val)

    def create_case_stack_vars(self, case_elem:CaseElement):
        self.declaration_map[case_elem] = self.create_reg(True)
        self.cur_tacfunc.append(TacAlloc(case_elem.get_type(), self.declaration_map[case_elem]))
        self.create_stack_vars(case_elem.expr)
        pass

    def create_stack_vars(self, exp:Expression) -> None:
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
        
        if not isinstance(exp, (Variable, Assign)):
            self.declaration_map[exp] = self.create_reg(True)
            self.cur_tacfunc.append(TacAlloc(exp.exp_type, self.declaration_map[exp]))

    def tacgen_exp(self, exp:Expression) -> TacReg:
        if isinstance(exp, Binop):
            #rhs_reg = self.tacgen_exp(exp.rhs)
            lhs_reg = self.tacgen_exp(exp.lhs)
            rhs_reg = self.tacgen_exp(exp.rhs)
            create_reg = self.create_reg()
            if isinstance(exp, (Plus, Minus, Times, Divide)):
                self.cur_tacfunc.append(TacCreate("Int", create_reg))
                self.cur_tacfunc.append(TacStore(create_reg, self.declaration_map[exp]))
                lhs_base = self.create_reg()
                lhs_prim = self.create_reg()
                self.cur_tacfunc.append(TacLoad(lhs_reg, lhs_base))
                self.cur_tacfunc.append(TacLoad(lhs_base, lhs_prim, 3))
                rhs_base = self.create_reg()
                rhs_prim = self.create_reg()
                self.cur_tacfunc.append(TacLoad(rhs_reg, rhs_base))
                self.cur_tacfunc.append(TacLoad(rhs_base, rhs_prim, 3))
                res_reg = self.create_reg()
                if isinstance(exp, Plus):
                    self.cur_tacfunc.append(TacAdd(lhs_prim, rhs_prim, res_reg))
                elif isinstance(exp, Minus):
                    self.cur_tacfunc.append(TacSub(lhs_prim, rhs_prim, res_reg))
                elif isinstance(exp, Times):
                    self.cur_tacfunc.append(TacMul(lhs_prim, rhs_prim, res_reg))
                elif isinstance(exp, Divide):
                    zero_reg = self.create_reg()
                    self.cur_tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
                    cmp_zero = self.create_reg()
                    self.cur_tacfunc.append(TacIcmp(TacCmpOp.EQ, zero_reg, rhs_prim, cmp_zero))
                    true_label = self.create_label()
                    false_label = self.create_label()
                    self.cur_tacfunc.append(TacBr(cmp_zero, true_label, false_label))
                    self.cur_tacfunc.append(true_label)
                    error_str = self.create_reg()
                    self.cur_tacfunc.append(TacLoadImm(TacStr(f"ERROR: {exp.lineno}: division by zero\\n"), error_str))
                    self.cur_tacfunc.append(TacSyscall("printf@PLT", [error_str], self.create_reg()))
                    one_reg = self.create_reg()
                    self.cur_tacfunc.append(TacLoadImm(TacImm(0), one_reg))
                    self.cur_tacfunc.append(TacSyscall("exit@PLT", [one_reg], self.create_reg()))
                    self.cur_tacfunc.append(TacUnreachable())
                    self.cur_tacfunc.append(false_label)
                    self.cur_tacfunc.append(TacDiv(lhs_prim, rhs_prim, res_reg))
                temp_reg = self.create_reg()
                self.cur_tacfunc.append(TacLoad(self.declaration_map[exp], temp_reg))
                self.cur_tacfunc.append(TacStore(res_reg, temp_reg, 3))
                self.cur_tacfunc.append(TacStore(temp_reg, self.declaration_map[exp]))
            else:
                self.cur_tacfunc.append(TacCreate("Bool", create_reg))
                self.cur_tacfunc.append(TacStore(create_reg, self.declaration_map[exp]))
                lhs_val = self.create_reg()
                rhs_val = self.create_reg()
                res_reg = self.create_reg()
                if exp.lhs.exp_type in {"Bool", "Int", "String"}:
                    self.cur_tacfunc.append(TacLoad(lhs_reg, lhs_val, 3))
                    self.cur_tacfunc.append(TacLoad(rhs_reg, rhs_val, 3))
                else:
                    self.cur_tacfunc.append(TacLoad(lhs_reg, lhs_val))
                    self.cur_tacfunc.append(TacLoad(rhs_reg, rhs_val))
                
                if isinstance(exp, Lt):
                    self.cur_tacfunc.append(TacIcmp(TacCmpOp.LT, lhs_reg, rhs_reg, res_reg))
                elif isinstance(exp, Le):
                    self.cur_tacfunc.append(TacIcmp(TacCmpOp.LE, lhs_reg, rhs_reg, res_reg))
                else:
                    self.cur_tacfunc.append(TacIcmp(TacCmpOp.EQ, lhs_reg, rhs_reg, res_reg))
                
                temp_reg = self.create_reg()
                self.cur_tacfunc.append(TacLoad(self.declaration_map[exp], temp_reg))
                self.cur_tacfunc.append(TacStore(res_reg, temp_reg, 3))
                self.cur_tacfunc.append(TacStore(temp_reg, self.declaration_map[exp]))
            return self.declaration_map[exp]
        elif isinstance(exp, Integer):
            int_reg = self.create_reg()
            prim_int_val = self.create_reg()
            self.cur_tacfunc.append(TacCreate("Int", int_reg))
            self.cur_tacfunc.append(TacLoadImm(TacImm(int(exp.val)), prim_int_val))
            self.cur_tacfunc.append(TacStore(prim_int_val, int_reg, 3))
            self.cur_tacfunc.append(TacStore(int_reg, self.declaration_map[exp]))
            return self.declaration_map[exp]
        elif isinstance(exp, StringExp):
            str_reg = self.create_reg()
            prim_str_val = self.create_reg()
            self.cur_tacfunc.append(TacCreate("String", str_reg))
            # TODO maybe I dont need to replace the \n and \t
            self.cur_tacfunc.append(TacLoadImm(TacStr(exp.val), prim_str_val))
            self.cur_tacfunc.append(TacStore(prim_str_val, str_reg, 3))
            self.cur_tacfunc.append(TacStore(str_reg, self.declaration_map[exp]))
            return self.declaration_map[exp]
        elif isinstance(exp, Bool):
            bool_reg = self.create_reg()
            prim_bool_val = self.create_reg()
            self.cur_tacfunc.append(TacCreate("Bool", bool_reg))
            self.cur_tacfunc.append(TacLoadImm(TacImm(1 if exp.kind == "true" else 0)), prim_bool_val)
            self.cur_tacfunc.append(TacStore(prim_bool_val, bool_reg, 3))
            self.cur_tacfunc.append(TacStore(bool_reg, self.declaration_map[exp]))
            return self.declaration_map[exp]
        elif isinstance(exp, Dispatch):
            obj_reg = self.tacgen_exp(exp.obj) if exp.obj is not None else self.self_reg()
            param_regs = [obj_reg]
            for arg in exp.args:
                param_regs.append(self.tacgen_exp(arg))
            
            ret_reg = self.create_reg()
            func_str = f"{exp.class_type.name}.{exp.get_func_name()}" if exp.class_type is not None else exp.get_func_name()
            self.cur_tacfunc.append(TacCall(func_str, param_regs, ret_reg))
            self.cur_tacfunc.append(TacStore(ret_reg, self.declaration_map[exp]))
            return self.declaration_map[exp]
        elif isinstance(exp, Variable):
            var_name = exp.var.name
            if self.symbol_table[var_name]:
                return self.symbol_table[var_name][-1]

            temp_reg = self.create_reg()
            self.cur_tacfunc.append(TacLoad(self.symbol_table["self"][-1], temp_reg, self.attr_table[var_name]))
            return temp_reg
        elif isinstance(exp, New):
            dest_reg = self.create_reg()
            self.cur_tacfunc.append(TacCreate(exp.class_name.get_name(), dest_reg))
            self.cur_tacfunc.append(TacStore(dest_reg, self.declaration_map[exp]))
            return self.declaration_map[exp]
        elif isinstance(exp, UnaryOp):
            # TODO these unary operations are clearly wrong
            rhs_reg = self.tacgen_exp(exp.rhs)
            dest_reg = self.create_reg()
            if isinstance(exp, Negate):
                self.cur_tacfunc.append(TacNegate(rhs_reg, dest_reg))
            elif isinstance(exp, Not):
                self.cur_tacfunc.append(TacNot(rhs_reg, dest_reg))
            else:
                zero_reg = self.create_reg()
                self.cur_tacfunc.append(TacLoadImm(TacImm(0)), zero_reg)
                self.cur_tacfunc.append(TacIcmp(TacCmpOp.EQ, rhs_reg, zero_reg, dest_reg))
            self.cur_tacfunc.append(TacStore(dest_reg, self.declaration_map[exp]))
            return self.declaration_map[exp]
        elif isinstance(exp, If):
            true_label = self.create_label()
            false_label = self.create_label()
            end_label = self.create_label()
            cond_reg = self.tacgen_exp(exp.condition)
            self.cur_tacfunc.append(TacBr(cond_reg, true_label, false_label))

            self.cur_tacfunc.append(true_label)
            then_reg = self.tacgen_exp(exp.then_body)
            self.cur_tacfunc.append(TacStore(then_reg, self.declaration_map[exp]))
            self.cur_tacfunc.append(TacBr(true_label=end_label))

            self.cur_tacfunc.append(false_label)
            else_reg = self.tacgen_exp(exp.else_body)
            self.cur_tacfunc.append(TacStore(else_reg, self.declaration_map[exp]))
            self.cur_tacfunc.append(TacBr(true_label=end_label))
            self.cur_tacfunc.append(end_label)

            return self.declaration_map[exp]
        elif isinstance(exp, While):
            while_start = self.create_label()
            while_body = self.create_label()
            while_end = self.create_label()
            self.cur_tacfunc.append(TacBr(true_label=while_start))
            self.cur_tacfunc.append(while_start)
            cond_reg = self.tacgen_exp(exp.condition)
            self.cur_tacfunc.append(TacBr(cond_reg, while_body, while_end))

            self.cur_tacfunc.append(while_body)
            self.tacgen_exp(exp.while_body)
            self.cur_tacfunc.append(TacBr(true_label=while_start))

            self.cur_tacfunc.append(while_end)
            return self.declaration_map[exp]
        elif isinstance(exp, Block):
            #TODO this is probably wrong
            for expr in exp.body:
                ret_reg = self.tacgen_exp(expr)
            return ret_reg
        elif isinstance(exp, Assign):
            rhs_reg = self.tacgen_exp(exp.rhs)
            temp_reg = self.create_reg()
            self.cur_tacfunc.append(TacLoad(rhs_reg, temp_reg))

            if self.symbol_table[exp.lhs.name]:
                self.cur_tacfunc.append(TacStore(temp_reg, self.symbol_table[exp.lhs.name][-1]))
                return self.symbol_table[exp.lhs.name][-1]
            
            self.cur_tacfunc.append(TacStore(temp_reg, self.attr_table[exp.lhs.name]))
            return self.attr_table[exp.lhs.name]
        elif isinstance(exp, Let):
            # adding additional registers into the symbol table
            for let_binding in exp.binding_list:
                binding_name = let_binding.var.name
                self.symbol_table[binding_name].append(self.declaration_map[let_binding])
                if let_binding.has_init():
                    init_res = self.tacgen_exp(let_binding.val)
                    self.cur_tacfunc.append(TacStore(init_res, self.declaration_map[let_binding]))
            
            ret_reg = self.tacgen_exp(exp.expr)

            for let_binding in exp.binding_list:
                self.symbol_table[let_binding.var.name].pop()
            
            return ret_reg

        elif isinstance(exp, Case):
            # set up the branches
            case_labels = [self.create_label() for _ in exp.case_list]
            error_label = self.create_label()
            case_end = self.create_label()
            ret_reg = self.create_reg(True)
            self.cur_tacfunc.append(TacDeclare(exp.exp_type, ret_reg))
            cur_obj = self.tacgen_exp(exp.case_expr)

            # load in the classtag
            class_tag = self.create_reg()
            self.cur_tacfunc.append(TacLoad(cur_obj, class_tag, 0))
            
            # do comparison with classtags
            for i, case_elem in enumerate(exp.case_list):
                false_label = self.create_label()
                case_class_tag = self.create_reg()
                self.cur_tacfunc.append(TacLoadImm(TacImm(self.class_tags[case_elem.get_type()]), case_class_tag, 0))
                branch_reg = self.create_reg()
                self.cur_tacfunc.append(TacIcmp(TacCmpOp.EQ, case_class_tag, class_tag, branch_reg))
                self.cur_tacfunc.append(TacBr(branch_reg, case_labels[i], false_label))
                self.cur_tacfunc.append(false_label)

            # if we fell through, we now need to generate an error condition
            # TODO later

            # now generate the case expression labels
            for i, case_elem in enumerate(exp.case_list):
                self.cur_tacfunc.append(case_labels[i])
                elem_reg = self.tacgen_exp(case_elem.expr)
                self.cur_tacfunc.append(TacStore(elem_reg, ret_reg, 0))
                self.cur_tacfunc.append(TacBr(true_label=end_label))

            self.cur_tacfunc.append(case_end)
            return ret_reg

    def debug_tac(self) -> None:
        for func in self.processed_funcs:
            print(repr(func))

    def get_tacfuncs(self) -> List[TacFunc]:
        return self.processed_funcs
