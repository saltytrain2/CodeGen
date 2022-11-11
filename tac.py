from __future__ import annotations
from tacnodes import *


class Tac(object):
    class_map:Dict[str, List[ClassAttribute]] = defaultdict(list)
    impl_map:Dict[str, List[ImplMethod]] = defaultdict(list)
    parent_map:Dict[str, str] = defaultdict(str)
    symbol_table:Dict[str, List[TacReg]] = defaultdict(list)
    class_tags:Dict[str, int] = defaultdict(int)
    attr_table:Dict[str, int] = defaultdict(int)

    def __init__(self, class_map:List[ClassMapEntry], impl_map:List[ImplMapEntry],
            parent_map:List[ParentMapEntry], ast:List[Class]):
        count = 0
        for entry in class_map:
            self.class_map[entry.class_name] = entry.attr_list
            self.class_tags[entry.class_name] = count
            count += 1
        
        for entry in impl_map:
            self.impl_map[entry.class_name] = entry.method_list

        for entry in parent_map:
            self.parent_map[entry.child] = entry.parent

        self.ast = ast
        self.processed_funcs = []
        self.cur_tacfunc = None
        self.num = 0
        self.symbol_table["self"].append(self.create_reg())

    def tacgen(self) -> None:
        for c in self.impl_map:
            offset = 3
            for attr in self.class_map[c]:
                self.attr_table[attr.get_name()] = offset
                offset += 1

            self.tacgen_constructor(c)
            for method in self.impl_map[c]:
                if method.parent != c or c in {"Object", "Bool", "String", "Int", "IO"}:
                    continue
                self.tacgen_func(method)
            
            self.attr_table.clear()

    def create_reg(self) -> TacReg:
        temp = TacReg(self.num)
        self.num += 1
        return temp
    
    def create_label(self) -> TacLabel:
        temp = TacLabel(self.num)
        self.num += 1
        return temp

    def tacgen_constructor(self, c:str):
        temp_num = self.num
        self.cur_tacfunc = TacFunc(f"{c}..new", None)
        obj_reg = self.create_reg()
        temp_reg = self.create_reg()
        size = 8 * len(self.class_map[c]) + 24
        self.cur_tacfunc.append(TacDeclare(c, obj_reg))
        self.cur_tacfunc.append(TacCall("malloc", [TacImm(size)], temp_reg))
        self.cur_tacfunc.append(TacStore(temp_reg, obj_reg))

        # store class_tag, obj_size, and vtable
        self.cur_tacfunc.append(TacStore(TacImm(self.class_tags[c]), obj_reg, 0))
        self.cur_tacfunc.append(TacStore(TacImm(size), obj_reg, 1))
        self.cur_tacfunc.append(TacStore(TacImm(f"{c}..vtable"), obj_reg, 2))

        for attr in self.class_map[c]:
            reg = self.create_reg()
            self.cur_tacfunc.append(TacDeclare(attr.attr_type, reg))
            if attr.attr_type in {"Bool", "Int", "String"}:
                temp_reg = self.create_reg()
                self.cur_tacfunc.append(TacCreate(attr.attr_type, temp_reg))
                self.cur_tacfunc.append(TacStore(temp_reg, reg))
            self.cur_tacfunc.append(TacStore(reg, obj_reg, self.attr_table[attr.get_name()]))
        
        ret_reg = self.create_reg()
        self.cur_tacfunc.append(TacLoad(obj_reg, ret_reg))
        self.cur_tacfunc.append(TacRet(ret_reg))

        self.processed_funcs.append(self.cur_tacfunc)
        self.num = temp_num

    def tacgen_func(self, method:ImplMethod) -> None:
        temp_num = self.num
        params:List[TacReg] = [self.symbol_table["self"][-1]]
        for param in method.get_formal_list():
            param_reg = self.create_reg()
            self.symbol_table[param].append(param_reg)
            params.append(param_reg)

        self.cur_tacfunc = TacFunc(f"{method.parent}.{method.get_name()}", params)
        ret_reg = self.tacgen_exp(method.expr)
        self.cur_tacfunc.append(TacRet(ret_reg))
        self.processed_funcs.append(self.cur_tacfunc)

        for param in method.get_formal_list():
            self.symbol_table[param].pop()

        self.num = temp_num

    def tacgen_exp(self, exp:Expression) -> TacReg:
        if isinstance(exp, Binop):
            lhs_reg = self.tacgen_exp(exp.lhs)
            rhs_reg = self.tacgen_exp(exp.rhs)
            ret_reg = self.create_reg()
            if isinstance(exp, (Plus, Minus, Times, Divide)):
                self.cur_tacfunc.append(TacCreate("Int", ret_reg))
                lhs_prim = self.create_reg()
                rhs_prim = self.create_reg()
                res_reg = self.create_reg()
                self.cur_tacfunc.append(TacLoad(lhs_reg, lhs_prim, 3))
                self.cur_tacfunc.append(TacLoad(rhs_reg, rhs_prim, 3))
                if isinstance(exp, Plus):
                    self.cur_tacfunc.append(TacAdd(lhs_reg, rhs_reg, res_reg))
                elif isinstance(exp, Minus):
                    self.cur_tacfunc.append(TacSub(lhs_reg, rhs_reg, res_reg))
                elif isinstance(exp, Times):
                    self.cur_tacfunc.append(TacMul(lhs_reg, rhs_reg, res_reg))
                elif isinstance(exp, Divide):
                    self.cur_tacfunc.append(TacDiv(lhs_reg, rhs_reg, res_reg))
                self.cur_tacfunc.append(TacStore(res_reg, ret_reg, 3))
            else:
                self.cur_tacfunc.append(TacCreate("Bool", ret_reg))
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
                
                self.cur_tacfunc.append(TacStore(res_reg, ret_reg, 3))
            return ret_reg
        elif isinstance(exp, Integer):
            int_reg = self.create_reg()
            self.cur_tacfunc.append(TacCreate("Int", int_reg))
            self.cur_tacfunc.append(TacStore(TacImm(int(exp.val)), int_reg, 3))
            return int_reg
        elif isinstance(exp, StringExp):
            str_reg = self.create_reg()
            self.cur_tacfunc.append(TacCreate("String", str_reg))
            self.cur_tacfunc.append(TacStore(TacStr(exp.val), str_reg, 3))
            return str_reg
        elif isinstance(exp, Bool):
            bool_reg = self.create_reg()
            self.cur_tacfunc.append(TacCreate("Bool", bool_reg))
            self.cur_tacfunc.append(TacStore(TacImm(1 if exp.kind == "true" else 0), bool_reg, 3))
            return bool_reg
        elif isinstance(exp, Dispatch):
            obj_reg = self.tacgen_exp(exp.obj) if exp.obj is not None else TacReg(0)
            param_regs = [obj_reg]
            for arg in exp.args:
                param_regs.append(self.tacgen_exp(arg))
            
            ret_reg = self.create_reg()
            func_str = f"{exp.class_type.name}.{exp.get_func_name()}" if exp.class_type is not None else exp.get_func_name()
            self.cur_tacfunc.append(TacCall(func_str, param_regs, ret_reg))
            return ret_reg
        elif isinstance(exp, Variable):
            var_name = exp.var.name
            attr_reg = self.create_reg()
            if var_name in self.attr_table:
                self.cur_tacfunc.append(TacLoad(TacReg(0), attr_reg, self.attr_table[var_name]))
            else:
                self.cur_tacfunc.append(TacLoad(self.symbol_table[exp.var.name][-1], attr_reg))
            return attr_reg
        elif isinstance(exp, New):
            dest_reg = self.create_reg()
            self.cur_tacfunc.append(TacCreate(exp.class_name.get_name(), dest_reg))
            return dest_reg
        elif isinstance(exp, UnaryOp):
            rhs_reg = self.tacgen_exp(exp.rhs)
            dest_reg = self.create_reg()
            if isinstance(exp, Negate):
                self.cur_tacfunc.append(TacNegate(rhs_reg, dest_reg))
            elif isinstance(exp, Not):
                self.cur_tacfunc.append(TacNot(rhs_reg, dest_reg))
            else:
                self.cur_tacfunc.append(TacIsVoid(rhs_reg, dest_reg))
            return dest_reg
        elif isinstance(exp, If):
            true_label = self.create_label()
            false_label = self.create_label()
            end_label = self.create_label()
            res_reg = self.create_reg()
            self.cur_tacfunc.append(TacDeclare(exp.exp_type, res_reg))
            cond_reg = self.tacgen_exp(exp.condition)
            self.cur_tacfunc.append(TacBr(cond_reg, true_label, false_label))

            self.cur_tacfunc.append(true_label)
            then_reg = self.tacgen_exp(exp.then_body)
            self.cur_tacfunc.append(TacStore(then_reg, res_reg))
            self.cur_tacfunc.append(TacBr(true_label=end_label))

            self.cur_tacfunc.append(false_label)
            else_reg = self.tacgen_exp(exp.else_body)
            self.cur_tacfunc.append(TacStore(else_reg, res_reg))
            self.cur_tacfunc.append(TacBr(true_label=end_label))
            self.cur_tacfunc.append(end_label)

            ret_reg = self.create_reg()
            self.cur_tacfunc.append(TacLoad(res_reg, ret_reg))
            return ret_reg
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
            ret_reg = self.create_reg()
            self.cur_tacfunc.append(TacDeclare("Object", ret_reg))
            return ret_reg
        elif isinstance(exp, Block):
            for expr in exp.body:
                ret_reg = self.tacgen_exp(expr)
            return ret_reg
        elif isinstance(exp, Assign):
            rhs_reg = self.tacgen_exp(exp.rhs)
            # maintain SSA by updating symbol table on every assignment
            # or by storing the value in assignment
            ret_reg = self.create_reg()
            if self.attr_table[exp.lhs.name]:
                self.cur_tacfunc.append(TacStore(rhs_reg, TacReg(0), self.attr_table[exp.lhs.name]))
                self.cur_tacfunc.append(TacLoad(TacReg(0), ret_reg, self.attr_table[exp.lhs.name]))
                #self.cur_tacfunc.append(TacStore(rhs_reg, TacReg(0), self.attr_table[exp.lhs.name]))
            else:
                self.cur_tacfunc.append(TacStore(rhs_reg, self.symbol_table[exp.lhs.name][-1]))
                self.cur_tacfunc.append(TacLoad(self.symbol_table[exp.lhs.name][-1], ret_reg))
                #self.symbol_table[exp.lhs.get_name()][-1] = rhs_reg
            return ret_reg
        elif isinstance(exp, Let):
            # adding additional registers into the symbol table
            for let_binding in exp.binding_list:
                binding_reg = self.create_reg()
                self.symbol_table[let_binding.var.name].append(binding_reg)
                self.cur_tacfunc.append(TacDeclare(let_binding.var_type.name, binding_reg))
                if let_binding.has_init():
                    init_res = self.tacgen_exp(let_binding.val)
                    self.cur_tacfunc.append(TacStore(init_res, binding_reg))
            
            ret_reg = self.tacgen_exp(exp.expr)

            for let_binding in exp.binding_list:
                self.symbol_table[let_binding.var.name].pop()
            
            return ret_reg

        elif isinstance(exp, Case):
            # set up the branches
            case_labels = [self.create_label() for _ in exp.case_list]
            error_label = self.create_label()
            case_end = self.create_label()
            ret_reg = self.create_reg()
            self.cur_tacfunc.append(TacDeclare(exp.exp_type, ret_reg))
            cur_obj = self.tacgen_exp(exp.case_expr)

            # load in the classtag
            class_tag = self.create_reg()
            self.cur_tacfunc.append(TacLoad(cur_obj, class_tag, 0))
            
            # do comparison with classtags
            for i, case_elem in enumerate(exp.case_list):
                false_label = self.create_label()
                case_class_tag = self.create_reg()
                self.cur_tacfunc.append(TacLoad(TacImm(self.class_tags[case_elem.get_type()]), case_class_tag, 0))
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