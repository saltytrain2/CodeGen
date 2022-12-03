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
    LOADIMM = auto()
    LOADSTR = auto()
    DECLARE = auto()
    CREATE = auto()
    LABEL = auto()
    SYSCALL = auto()
    GEP = auto()
    UNREACHABLE = auto()
    ALLOC = auto()
    STORESELF = auto()
    CMP = auto()


class TacCmpOp(Enum):
    EQ = auto()
    LE = auto()
    LT = auto()
    NE = auto()


class TacFunc:
    def __init__(self, name:str, params:List[TacReg]=None, insts:List[TacValue]=None, space:int=0, callee_save:List[PReg]=None) -> None:
        self.name = name
        self.params = params if params is not None else []
        self.insts = insts if insts is not None else []
        self.stack_space = space
        self.self_reg = None
        self.callee_saved = callee_save if callee_save is not None else []

    def __repr__(self) -> str:
        insts_repr = []
        for inst in self.insts:
            insts_repr.append(repr(inst))
        formal_str = "".join(insts_repr)

        return f"{self.name}({', '.join(repr(param) for param in self.params)}) {self.stack_space}\n{formal_str}"
        raise NotImplementedError

    def append(self, tacnode:TacInst) -> None:
        self.insts.append(tacnode)

    def replace(self, tacinst:TacInst, index) -> None:
        self.insts[index] = tacinst
    
    def set_stack_space(self, space:int) -> None:
        self.stack_space = space

    def set_self_reg(self, self_reg:TacReg) -> None:
        self.self_reg = self_reg
    pass

class PReg(object):
    def __init__(self, name:str, offset:int=None):
        self.name = name
        self.offset = offset

    def __repr__(self) -> str:
        offset_str = f"+{self.offset}" if self.offset is not None else ""
        return f"{self.name}{offset_str}"

    def __eq__(self, other) -> bool:
        return isinstance(other, PReg) and self.name == other.name and self.offset == other.offset

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.name)

    def get_name(self) -> str:
        if self.offset is not None:
            return f"{self.offset}({self.name})"
        return self.name

    def get_32_name(self) -> str:
        if self.name[2].isdigit():
            reg_32_str = self.name + "d"
        else:
            reg_32_str = "%e" + self.name[2:]

        if self.offset is not None:
            return f"{self.offset}({reg_32_str})"

        return reg_32_str

    def get_offset(self) -> int:
        return int(self.offset)
    
    pass


class TacValue(object):
    def __init__(self):
        self.physical_reg:PReg = None
    
    def set_preg(self, reg:PReg) -> None:
        self.physical_reg = reg
    
    def get_preg(self) -> PReg:
        return self.physical_reg

    def get_preg_str(self) -> str:
        return self.physical_reg.get_name()
    
    def get_preg_32_str(self) -> str:
        return self.physical_reg.get_32_name()
    
    def get_preg_offset(self) -> str:
        return self.physical_reg.get_offset()
    pass


class TacReg(TacValue):
    def __init__(self, num:int, isstack:bool=False):
        super().__init__()
        self.num = num
        self.isstack = isstack
        self.live_start = None
        self.live_end = None

    def __repr__(self) -> str:
        return "%" + str(self.num)

    def __eq__(self, other) -> bool:
        return isinstance(other, TacReg) and self.num == other.num

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.num)

    def set_live_start(self, start:int) -> None:
        self.live_start = start
    
    def set_live_end(self, end:int) -> None:
        self.live_end = end


class TacImm(object):
    def __init__(self, val:int):
        super().__init__()
        self.val = val

    def __repr__(self) -> str:
        return "$" + str(self.val)


class TacStr(TacImm):
    def __init__(self, val:str):
        super().__init__(val)

    def __repr__(self) -> str:
        return self.val

class TacImmLabel(TacImm):
    def __init__(self, label:str):
        super().__init__(label)

    def __repr__(self) -> str:
        return self.val

class TacErrorStr(TacImm):
    def __init__(self, val:str):
        super().__init__(val)

    def __repr__(self) -> str:
        return self.val


class TacInst(object):
    def __init__(self, op:TacOp, livegen:Set[TacValue]=None, livekill:Set[TacValue]=None):
        self.op = op
        self.livegen = {i for i in livegen if isinstance(i, TacReg) and not i.isstack} if livegen is not None else set()
        self.livekill = {i for i in livekill if isinstance(i, TacReg) and not i.isstack} if livekill is not None else set()
        self.live_in = set()
        self.live_out = set()

    def __repr__(self) -> str:
        return self.op.name.lower()
    
    def get_live_out(self) -> Set[TacReg]:
        return self.live_out
    
    def get_live_in(self) -> Set[TacReg]:
        return self.live_in
    
    def get_intersection(self) -> Set[TacReg]:
        return set.union(self.live_out, self.live_in)

    def update_live_set(self, succ_live_in:Set[TacReg]) -> bool:
        old_live_in = self.live_in.copy()
        old_live_out = self.live_out.copy()
        self.live_out = succ_live_in.copy()
        self.live_in = self.livegen.union(self.live_out.difference(self.livekill))
        return old_live_in != self.live_in or old_live_out != self.live_out


class TacLabel(TacInst):
    def __init__(self, num:int):
        super().__init__(TacOp.LABEL)
        self.num = num

    def __repr__(self) -> str:
        return f"{self.num}:\n"

    def __eq__(self, other) -> bool:
        return isinstance(other, TacLabel) and self.num == other.num

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.num)


class TacUnaryOp(TacInst):
    def __init__(self, op:TacOp, src:TacReg, dest:TacReg):
        super().__init__(op, {src}, {dest})
        self.src = src
        self.dest = dest

    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = {super().__repr__()} {repr(self.src)}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"


class TacBinOp(TacInst):
    def __init__(self, op:TacOp, src1:TacReg, src2:TacReg, dest:TacReg):
        super().__init__(op, {src1, src2}, {dest})
        self.src1 = src1
        self.src2 = src2
        self.dest = dest

    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = {super().__repr__()} {repr(self.src1)} {repr(self.src2)}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"


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
    def __init__(self, cmp_op:TacCmpOp=None, true_label:TacLabel=None, false_label:TacLabel=None):
        super().__init__(TacOp.BR, None, None)
        self.cond = cmp_op
        self.true_label = true_label
        self.false_label = false_label

    def __repr__(self) -> str:
        if self.cond is None:
            inst_str = f"br label %{self.true_label.num}"
        else:
            inst_str = f"br {repr(self.cond.name)} label %{self.true_label.num} label %{self.false_label.num}"

        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"
    
    def get_branch_targets(self) -> List[TacLabel]:
        labels = [self.true_label]
        if self.false_label is not None:
            labels.append(self.false_label)

        return labels


class TacIcmp(TacInst):
    def __init__(self, icmp_op:TacCmpOp, src1:TacReg, src2:TacReg, dest:TacReg):
        super().__init__(TacOp.ICMP, {src1, src2}, {dest})
        self.icmp_op = icmp_op
        self.src1 = src1
        self.src2 = src2
        self.dest = dest
    
    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = icmp {self.icmp_op.name.lower()} {repr(self.src1)} {repr(self.src2)}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"

class TacCmp(TacInst):
    def __init__(self, src1:TacReg, src2:TacReg):
        super().__init__(TacOp.ICMP, {src1, src2}, {})
        self.src1 = src1
        self.src2 = src2
    
    def __repr__(self) -> str:
        inst_str = f"cmp {repr(self.src1)} {repr(self.src2)}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"

class TacCall(TacInst):
    def __init__(self, func:str, args:List[TacReg], dest:TacReg, offset:int=None):
        super().__init__(TacOp.CALL, {arg for arg in args}, {dest})
        self.func = func
        self.args = args
        self.dest = dest
        self.save_regs:List[PReg] = []
        self.offset = offset

    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = call {self.func}({', '.join(repr(arg) for arg in self.args)})"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"
        raise NotImplementedError

    def set_save_regs(self, save_regs:List[PReg]):
        self.save_regs = save_regs
    


class TacRet(TacInst):
    def __init__(self, src:TacReg):
        super().__init__(TacOp.RET, {src}, None)
        self.src = src

    def __repr__(self) -> str:
        inst_str = f"ret {repr(self.src)}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"
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
        super().__init__(TacOp.LOAD, {src}, {dest})
        self.src = src
        self.dest = dest
        self.offset = offset

    def __repr__(self) -> str:
        offset_str = f"[{str(self.offset)}]" if self.offset else ""
        inst_str = f"{repr(self.dest)} = load {repr(self.src)}{offset_str}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"


class TacLoadImm(TacInst):
    def __init__(self, imm:TacImm, dest:TacReg):
        super().__init__(TacOp.LOADIMM, None, {dest})
        self.dest = dest
        self.imm = imm

    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = load {repr(self.imm)}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"


class TacLoadStr(TacInst):
    def __init__(self, dest:TacReg, string:TacStr):
        super().__init__(TacOp.LOADSTR, None, {dest})
        self.dest = dest
        self.string = string
    
    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = load {repr(self.string)}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"


class TacStore(TacInst):
    def __init__(self, src:TacReg, dest:TacReg, offset:int=None):
        super().__init__(TacOp.STORE, {src, dest}, None)
        self.src = src
        self.dest = dest
        self.offset = offset
    
    def __repr__(self) -> str:
        offset_str = f"[{str(self.offset)}]" if self.offset else ""
        inst_str = f"store {repr(self.src)} {repr(self.dest)}{offset_str}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"


class TacCreate(TacInst):
    def __init__(self, object:str, dest:TacReg):
        super().__init__(TacOp.CREATE, None, {dest})
        self.object = object
        self.dest = dest
        self.args = []
        self.save_regs:List[PReg] = []
        self.self_reg:TacReg = None

    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = create {self.object}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"
    
    def get_object(self) -> str:
        return self.object

    def set_self_reg(self, self_reg:TacReg) -> str:
        self.self_reg = self_reg

class TacDeclare(TacInst):
    def __init__(self, object:str, dest:TacReg):
        super().__init__(TacOp.DECLARE, None, {dest})
        self.object = object
        self.dest = dest

    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = declare {self.object}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"
    
    def get_object(self) -> str:
        return self.object


class TacSyscall(TacInst):
    def __init__(self, func:str, args:List[TacReg], dest:TacReg):
        super().__init__(TacOp.SYSCALL, {arg for arg in args}, {dest})
        self.func = func
        self.args = args
        self.dest = dest
        self.save_regs:List[PReg] = []

    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = syscall {self.func}({', '.join(repr(arg) for arg in self.args)})"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"

    def set_save_regs(self, save_regs:List[PReg]):
        self.save_regs = save_regs


class TacGep(TacInst):
    def __init__(self, src:TacReg, dest:TacReg, offset:int):
        super().__init__(TacOp.GEP, {src}, {dest})
        self.src = src
        self.dest = dest
        self.offset = offset
    
    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = getelementptr {repr(self.src)}[{self.offset}]"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"


class TacUnreachable(TacInst):
    def __init__(self):
        super().__init__(TacOp.UNREACHABLE, None, None)

    def __repr__(self) -> str:
        return "unreachable\n"


class TacAlloc(TacInst):
    def __init__(self, obj:str, dest:TacReg):
        super().__init__(TacOp.ALLOC, None, {dest})
        self.obj = obj
        self.dest = dest

    def __repr__(self) -> str:
        inst_str = f"{repr(self.dest)} = alloc {self.obj}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"

class TacStoreSelf(TacInst):
    """
    Special store that puts the self object into the preallocated self register
    """
    def __init__(self, self_obj:TacReg, dest:TacReg):
        super().__init__(TacOp.STORESELF, {self_obj}, {dest})
        self.self_obj = self_obj
        self.dest = dest

    def __repr__(self) -> str:
        inst_str = f"store self {self.self_obj} {repr(self.dest)}"
        return f"{inst_str:<75} ; live: {repr(self.live_out) if self.live_out else ''}\n"