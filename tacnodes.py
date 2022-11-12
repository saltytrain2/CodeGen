from __future__ import annotations
from enum import Enum, auto
from typing import List
from coolast import *
from collections import defaultdict

class TacOp(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    ICMP = auto()
    BR = auto()
    CALL = auto()
    NOT = auto()
    RET = auto()
    ISVOID = auto()
    STRING = auto()
    INT = auto()
    BOOL = auto()
    ASSIGN = auto()
    LOAD = auto()
    STORE = auto()
    DECLARE = auto()
    CREATE = auto()
    LABEL = auto()


class TacCmpOp(Enum):
    EQ = auto()
    LE = auto()
    LT = auto()


class TacFunc:
    def __init__(self, name:str, params:List[TacReg]=None, insts:List[TacValue]=None):
        self.name = name
        self.params = params if params is not None else []
        self.insts = insts if insts is not None else []

    def __repr__(self) -> str:
        insts_repr = []
        for inst in self.insts:
            insts_repr.append(repr(inst))
        formal_str = "".join(insts_repr)

        return f"{self.name}{str(self.params)}\n{formal_str}"
        raise NotImplementedError

    def append(self, tacnode:TacInst) -> None:
        self.insts.append(tacnode)

    pass

class PReg(object):
    def __init__(self, name:str, offset:int=None):
        self.name = name
        self.offset = offset

    def __repr__(self) -> str:
        offset_str = f"+{self.offset}" if self.offset is not None else ""
        return f"{self.name}{offset_str}"
    pass


class TacValue(object):
    # def __init__(self, val:any):
    #     self.val 
    #     self.physical_reg = None
    
    # def set_reg(self, reg:str) -> None:
    #     self.physical_reg = reg
    
    # def get_reg(self) -> str:
    #     return self.physical_reg
    pass


class TacReg(TacValue):
    def __init__(self, num:int):
        self.num = num
        self.physical_reg:PReg = None

    def __repr__(self) -> str:
        return "%" + str(self.num)

    def __eq__(self, other) -> bool:
        return isinstance(other, TacReg) and self.num == other.num

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.num)

    def set_physical_reg(self, reg:PReg) -> None:
        self.physical_reg = reg
    
    def get_physical_reg(self) -> PReg:
        return self.physical_reg


class TacImm(TacValue):
    def __init__(self, val:int):
        self.val = val

    def __repr__(self) -> str:
        return str(self.val)


class TacStr(TacValue):
    def __init__(self, val:str):
        self.val = val

    def __repr__(self) -> str:
        return f"\"{self.val}\""


class TacInst(object):
    def __init__(self, op:TacOp):
        self.op = op

    def __repr__(self) -> str:
        return self.op.name.lower()
    
    def get_live_regs(self) -> List[TacReg]:
        raise NotImplementedError
    
    def get_dead_reg(self) -> TacReg:
        raise NotImplementedError


class TacLabel(TacInst):
    def __init__(self, num:int):
        super().__init__(TacOp.LABEL)
        self.num = num

    def __repr__(self) -> str:
        return f"{self.num}:\n"


class TacUnaryOp(TacInst):
    def __init__(self, op:TacOp, src:TacReg, dest:TacReg):
        super().__init__(op)
        self.src = src
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = {super().__repr__()} {repr(self.src)}\n"


class TacBinOp(TacInst):
    def __init__(self, op:TacOp, src1:TacReg, src2:TacReg, dest:TacReg):
        super().__init__(op)
        self.src1 = src1
        self.src2 = src2
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = {super().__repr__()} {repr(self.src1)} {repr(self.src2)}\n"


class TacAdd(TacBinOp):
    def __init__(self, src1:TacReg, src2:TacReg, dest:TacReg):
        super().__init__(TacOp.ADD, src1, src2, dest)

    def __repr__(self) -> str:
        return super().__repr__()
    
    def gen_x86_unopt(self) -> str:

        pass


class TacSub(TacBinOp):
    def __init__(self, src1:TacReg, src2:TacReg, dest:TacReg):
        super().__init__(TacOp.SUB, src1, src2, dest)

    def __repr__(self) -> str:
        return super().__repr__()


class TacMul(TacBinOp):
    def __init__(self, src1:TacReg, src2:TacReg, dest:TacReg):
        super().__init__(TacOp.MUL, src1, src2, dest)

    def __repr__(self) -> str:
        return super().__repr__()


class TacDiv(TacBinOp):
    def __init__(self, src1:TacReg, src2:TacReg, dest:TacReg):
        super().__init__(TacOp.DIV, src1, src2, dest)

    def __repr__(self) -> str:
        return super().__repr__()


class TacBr(TacInst):
    def __init__(self, cond:TacReg=None, true_label:TacLabel=None, false_label:TacLabel=None):
        super().__init__(TacOp.BR)
        self.cond = cond
        self.true_label = true_label
        self.false_label = false_label

    def __repr__(self) -> str:
        if self.cond is None:
            return f"br label %{self.true_label.num}\n"
        else:
            return f"br {repr(self.cond)} label %{self.true_label.num} label %{self.false_label.num}\n"
    
    def get_branch_targets(self) -> List[TacLabel]:
        labels = [self.true_label]
        if self.false_label is not None:
            labels.append(self.false_label)

        return labels


class TacIcmp(TacInst):
    def __init__(self, icmp_op:TacCmpOp, src1:TacReg, src2:TacReg, dest:TacReg):
        super().__init__(TacOp.ICMP)
        self.icmp_op = icmp_op
        self.src1 = src1
        self.src2 = src2
        self.dest = dest
    
    def __repr__(self) -> str:
        return f"{repr(self.dest)} = icmp {self.icmp_op.name.lower()} {repr(self.src1)} {repr(self.src2)}\n"


class TacCall(TacInst):
    def __init__(self, func:str, args:List[TacReg], dest:TacReg):
        super().__init__(TacOp.CALL)
        self.func = func
        self.args = args
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = call {self.func}{str(self.args)}\n"
        raise NotImplementedError


class TacRet(TacInst):
    def __init__(self, src:TacReg):
        super().__init__(TacOp.RET)
        self.src = src

    def __repr__(self) -> str:
        return f"ret {repr(self.src)}\n"
        raise NotImplementedError


class TacNot(TacUnaryOp):
    def __init__(self, src:TacReg, dest:TacReg):
        super().__init__(TacOp.NOT, src, dest)
        self.src = src
        self.dest = dest

    def __repr__(self) -> str:
        return super().__repr__()
        raise NotImplementedError


class TacNegate(TacUnaryOp):
    def __init__(self, src:TacReg, dest:TacReg):
        super().__init__(TacOp.NOT, src, dest)

    def __repr__(self) -> str:
        return super().__repr__()
        raise NotImplementedError


class TacIsVoid(TacUnaryOp):
    def __init__(self, src:TacReg, dest:TacReg):
        super().__init__(TacOp.ISVOID, src, dest)

    def __repr__(self) -> str:
        return super().__repr__()
        raise NotImplementedError


class TacLoad(TacInst):
    def __init__(self, src:TacReg, dest:TacReg, offset:int=None):
        super().__init__(TacOp.LOAD)
        self.src = src
        self.dest = dest
        self.offset = offset

    def __repr__(self) -> str:
        offset_str = f"[{str(self.offset)}]" if self.offset is not None else ""
        return f"{repr(self.dest)} = load {repr(self.src)}{offset_str}\n"


class TacStore(TacInst):
    def __init__(self, src:TacReg, dest:TacReg, offset:int=None):
        super().__init__(TacOp.STORE)
        self.src = src
        self.dest = dest
        self.offset = offset
    
    def __repr__(self) -> str:
        offset_str = f"[{str(self.offset)}]" if self.offset is not None else ""
        return f"store {repr(self.src)} {repr(self.dest)}{offset_str}\n"


class TacCreate(TacInst):
    def __init__(self, object:str, dest:TacReg):
        super().__init__(TacOp.CREATE)
        self.object = object
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = create {self.object}\n"


class TacDeclare(TacInst):
    def __init__(self, object:str, dest:TacReg):
        super().__init__(TacOp.DECLARE)
        self.object = object
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = declare {self.object}\n"


"""
Actual Tac Class
"""
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

            return res_reg
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
