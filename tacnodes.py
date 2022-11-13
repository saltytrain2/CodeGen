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
    STRING = auto()
    INT = auto()
    BOOL = auto()
    ASSIGN = auto()
    LOAD = auto()
    STORE = auto()
    DECLARE = auto()
    CREATE = auto()
    LABEL = auto()
    SYSCALL = auto()


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
    physical_reg:PReg = None
    
    def set_preg(self, reg:PReg) -> None:
        self.physical_reg = reg
    
    def get_preg(self) -> PReg:
        return self.physical_reg
    pass


class TacReg(TacValue):
    def __init__(self, num:int):
        self.num = num

    def __repr__(self) -> str:
        return "%" + str(self.num)

    def __eq__(self, other) -> bool:
        return isinstance(other, TacReg) and self.num == other.num

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.num)


class TacImm(TacValue):
    def __init__(self, val:int):
        self.val = val

    def __repr__(self) -> str:
        return "$" + str(self.val)


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


class TacSyscall(TacInst):
    def __init__(self, func:str, args:List[TacReg], dest:TacReg):
        super().__init__(TacOp.SYSCALL)
        self.func = func
        self.args = args
        self.dest = dest

    def __repr__(self) -> str:
        return f"{repr(self.dest)} = call {self.func}{str(self.args)}\n"