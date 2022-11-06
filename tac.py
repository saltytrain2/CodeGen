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
    NEW = auto()
    ASSIGN = auto()


class TacCmpOp(Enum):
    EQ = auto()
    LE = auto()
    LT = auto()


class TacFunc:
    def __init__(self, name:str, insts:List[TacNode]=None):
        self.name = name
        self.insts = insts if insts is not None else []

    def __repr__(self) -> str:
        insts_repr = []
        for inst in self.insts:
            insts_repr.append(repr(inst))
        formal_str = "".join(insts_repr)

        return f"{self.name}\n{formal_str}"
        raise NotImplementedError

    def append(self, tacnode:TacNode) -> None:
        self.insts.append(tacnode)

    pass


class TacRegType():
    pass

class TacNode(object):
    pass

class TacReg(TacNode):
    def __init__(self, num: int):
        self.num = num

    def __repr__(self) -> str:
        return "%" + str(self.num)


class TacLabel(TacNode):
    def __init__(self, num: int):
        self.num = num

    def __repr__(self) -> str:
        return ".L" + str(self.num)


class TacInst:
    def __init__(self, op:TacOp):
        self.op = op

    def __repr__(self) -> str:
        return self.op.name.lower()


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
            return f"{self.op.name.lower()} {repr(self.true_label)}"
        else:
            return f"br {repr(self.cond)} {repr(self.true_label)} {repr(self.false_label)}\n"


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
    def __init__(self, func:str, obj:TacReg, args:List[TacReg], dest:TacReg):
        super().__init__(TacOp.CALL)
        self.func = func
        self.obj = obj
        self.args = args
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = call {repr(self.obj)} {self.func}{str(self.args)}\n"
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


class TacAssign(TacInst):
    def __init__(self, src:TacReg, dest:TacReg):
        super().__init__(TacOp.ASSIGN)
        self.src = src
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = {repr(self.src)}\n"
        raise NotImplementedError


class TacString(TacInst):
    def __init__(self, strval:str, dest:TacReg):
        super().__init__(TacOp.STRING)
        self.strval = strval
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = {self.strval}\n"


class TacInt(TacInst):
    def __init__(self, intval:int, dest:TacReg):
        super().__init__(TacOp.INT)
        self.intval = intval
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = {str(self.intval)}\n"


class TacBool(TacInst):
    def __init__(self, boolval:bool, dest:TacReg):
        super().__init__(TacOp.BOOL)
        self.boolval = boolval
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = {str(self.boolval)}\n"
        raise NotImplementedError


class TacNew(TacInst):
    def __init__(self, object:str, dest:TacReg):
        super().__init__(TacOp.NEW)
        self.object = object
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = new {self.object}\n"
        raise NotImplementedError




"""
Actual Tac Class
"""
class Tac(object):
    class_map:Dict[str, List[ClassAttribute]] = defaultdict(list)
    impl_map:Dict[str, List[ImplMethod]] = defaultdict(list)
    parent_map:Dict[str, str] = defaultdict(str)

    def __init__(self, class_map:List[ClassMapEntry], impl_map:List[ImplMapEntry],
            parent_map:List[ParentMapEntry], ast:List[Class]):
        for entry in class_map:
            self.class_map[entry.class_name] = entry.attr_list
        
        for entry in impl_map:
            self.impl_map[entry.class_name] = entry.method_list

        for entry in parent_map:
            self.parent_map[entry.child] = entry.parent

        self.ast = ast
        self.symbol_table:Dict[str, List[str]] = defaultdict(list)
        self.processed_funcs = []
        self.cur_tacfunc = None
        self.num = 0
        self.symbol_table["self"].append(self.create_reg())

    def tacgen(self) -> None:
        for c in self.impl_map:
            self.num = 1
            for attr in self.class_map[c]:
                self.symbol_table[attr.get_name()].append(self.create_reg())

            for method in self.impl_map[c]:
                if method.parent != c or c in {"Object", "Bool", "String", "Int", "IO"}:
                    continue

                self.tacgen_func(method)

            for attr in self.class_map[c]:
                self.symbol_table[attr.get_name()].pop()

    def create_reg(self) -> TacReg:
        temp = TacReg(self.num)
        self.num += 1
        return temp
    
    def create_label(self) -> TacLabel:
        temp = TacLabel(self.num)
        self.num += 1
        return temp

    def tacgen_func(self, method:ImplMethod) -> None:
        # self.num = 1
        temp_num = self.num
        for param in method.get_formal_list():
            self.symbol_table[param].append(self.create_reg())

        self.cur_tacfunc = TacFunc(f"{method.parent}.{method.get_name()}")
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
            dest_reg = self.create_reg()
            if isinstance(exp, Plus):
                self.cur_tacfunc.append(TacAdd(lhs_reg, rhs_reg, dest_reg))
            elif isinstance(exp, Minus):
                self.cur_tacfunc.append(TacSub(lhs_reg, rhs_reg, dest_reg))
            elif isinstance(exp, Times):
                self.cur_tacfunc.append(TacMul(lhs_reg, rhs_reg, dest_reg))
            elif isinstance(exp, Divide):
                self.cur_tacfunc.append(TacDiv(lhs_reg, rhs_reg, dest_reg))
            elif isinstance(exp, Lt):
                self.cur_tacfunc.append(TacIcmp(TacCmpOp.LT, lhs_reg, rhs_reg, dest_reg))
            elif isinstance(exp, Le):
                self.cur_tacfunc.append(TacIcmp(TacCmpOp.LE, lhs_reg, rhs_reg, dest_reg))
            else:
                self.cur_tacfunc.append(TacIcmp(TacCmpOp.EQ, lhs_reg, rhs_reg, dest_reg))
            return dest_reg
        elif isinstance(exp, Integer):
            int_reg = self.create_reg()
            self.cur_tacfunc.append(TacInt(int(exp.val), int_reg))
            return int_reg
        elif isinstance(exp, StringExp):
            str_reg = self.create_reg()
            self.cur_tacfunc.append(TacString(exp.val, str_reg))
            return str_reg
        elif isinstance(exp, Bool):
            bool_reg = self.create_reg()
            self.cur_tacfunc.append(TacBool(True if exp.kind == "true" else False, bool_reg))
            return bool_reg
        # elif isinstance(exp, Dispatch):
        #     obj_reg = self.tacgen_exp(exp.obj) if exp.obj is not None else TacReg(0)
        #     param_regs = []
        #     for arg in exp.args:
        #         param_regs.append(self.tacgen_exp(arg))
            
        #     ret_reg = self.create_reg()
        #     func_str = None
        #     self.cur_tacfunc.append(TacCall())
        #     pass
        elif isinstance(exp, DynamicDispatch):
            obj_reg = self.tacgen_exp(exp.obj)
            param_regs = []
            for arg in exp.args:
                param_regs.append(self.tacgen_exp(arg))
            
            return_reg = TacReg(self.num)
            self.num += 1
            
            self.cur_tacfunc.append(TacCall(exp.get_func_name(), obj_reg, param_regs, return_reg))
            return return_reg
        elif isinstance(exp, StaticDispatch):
            pass
        elif isinstance(exp, SelfDispatch):
            obj_reg = TacReg(0)
            param_regs = []
            for arg in exp.args:
                param_regs.append(self.tacgen_exp(arg))
            
            return_reg = TacReg(self.num)
            self.num += 1
            
            self.cur_tacfunc.append(TacCall(exp.get_func_name(), obj_reg, param_regs, return_reg))
            return return_reg
            # pass
        elif isinstance(exp, Variable):
            return self.symbol_table[exp.var.name][-1]
        elif isinstance(exp, New):
            dest_reg = self.create_reg()
            self.cur_tacfunc.append(TacNew(exp.class_name, dest_reg))
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
            self.cur_tacfunc.append(TacAssign(then_reg, res_reg))
            self.cur_tacfunc.append(TacBr(true_label=end_label))

            self.cur_tacfunc.append(false_label)
            else_reg = self.tacgen_exp(exp.else_body)
            self.cur_tacfunc.append(TacAssign(else_reg, res_reg))
            self.cur_tacfunc.append(TacBr(true_label=end_label))
            self.cur_tacfunc.append(end_label)

            return res_reg
        elif isinstance(exp, While):
            while_start = self.create_label()
            while_body = self.create_label()
            while_end = self.create_label()
            self.cur_tacfunc.append(while_start)
            cond_reg = self.tacgen_exp(exp.condition)
            self.cur_tacfunc.append(TacBr(cond_reg, while_body, while_end))

            self.cur_tacfunc.append(while_body)
            self.tacgen_exp(exp.while_body)
            self.cur_tacfunc.append(TacBr(true_label=while_start))

            self.cur_tacfunc.append(while_end)
            ret_reg = self.create_reg()
            self.cur_tacfunc.append(TacNew("Object", ret_reg))
            return ret_reg
        elif isinstance(exp, Block):
            for expr in exp.body:
                ret_reg = self.tacgen_exp(expr)
            return ret_reg
        elif isinstance(exp, Assign):
            rhs_reg = self.tacgen_exp(exp.rhs)
            lhs_reg = self.symbol_table[exp.lhs.name][-1]
            return lhs_reg

        elif isinstance(exp, Let):
            pass
        elif isinstance(exp, Case):
            pass

    def debug_tac(self) -> None:
        for func in self.processed_funcs:
            print(repr(func))