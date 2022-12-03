from __future__ import annotations
from typing import TYPE_CHECKING
from collections import defaultdict

from tac import *

if TYPE_CHECKING:
    from cfgnodes import CFGFunc, CFGBlock
    from typing import List, Dict, Set, Tuple, Optional


class FixedRegisterAllocator(object):
    def __init__(self, interference_graph:Dict[TacReg, Set[TacReg]]=None):
        self.return_reg:PReg = PReg("%rax")
        self.self_reg:PReg = PReg("%r12")
        self.caller_saved:List[PReg] = [
            PReg("%rdi"), PReg("%rsi"), PReg("%rdx"), PReg("%rcx"), PReg("%r8"), PReg("%r9"), PReg("%r10"), PReg("%r11"), PReg("%rax")
        ]
        self.callee_saved:List[PReg] = [
            PReg("%r12"), PReg("%rbx"), PReg("%r13"), PReg("%r14"), PReg("%r15")
        ]
        self.interference_graph = interference_graph if interference_graph is not None else defaultdict(set)
        self.physical_reg_map:Dict[PReg, List[TacReg]] = defaultdict(list)
        self.tac_reg_map:Dict[TacReg, PReg] = {}
        self.used_callee_regs: set[PReg] = set()
        self.reset()

    def get_caller_reg(self, input_reg:TacReg) -> PReg:
        for physical_reg in self.caller_saved[:-2]:
            # if the register is unused, great
            if not self.physical_reg_map[physical_reg]:
                self.physical_reg_map[physical_reg].append(input_reg)
                return physical_reg
            
            conflict = False
            for tac_reg in self.physical_reg_map[physical_reg]:
                # we can reuse the register since they do not overlap
                if tac_reg in self.interference_graph[input_reg]:
                    conflict = True
            
            if not conflict:
                self.physical_reg_map[physical_reg].append(input_reg)
                return physical_reg

        # we fell through, we found nothing
        return None

    def get_callee_reg(self, input_reg:TacReg) -> PReg:
        for physical_reg in self.callee_saved[1:]:
            # if the register is unused, yay
            if not self.physical_reg_map[physical_reg]:
                self.physical_reg_map[physical_reg].append(input_reg)
                return physical_reg
            
            conflict = False
            for tac_reg in self.physical_reg_map[physical_reg]:
                # we can reuse the register since they do not overlap
                if tac_reg in self.interference_graph[input_reg]:
                    conflict = True
            
            if not conflict:
                self.physical_reg_map[physical_reg].append(input_reg)
                return physical_reg
        # we fell through, we found nothing
        return None
    
    def get_caller_regs(self) -> Set[PReg]:
        return set(self.caller_saved)

    def get_callee_regs(self) -> Set[PReg]:
        return set(self.callee_saved)

    def add_used_reg(self, physical_reg:PReg, treg:TacReg) -> None:
        self.physical_reg_map[physical_reg].append(treg)
        if physical_reg in self.callee_saved:
            self.used_callee_regs.add(physical_reg)
    
    def get_unused_reg(self, tacreg:TacReg) -> None:
        # lets try to get a caller-saved register
        reg = self.get_callee_reg(tacreg)
        if reg is not None:
            self.used_callee_regs.add(reg)
            return reg

        reg = self.get_caller_reg(tacreg)
        if reg is not None:
            return reg

        raise Exception("We ran out of regs, you need to start spilling to memory")

    def reset(self) -> None:
        self.physical_reg_map.clear()
        self.tac_reg_map.clear()

    def construct_tac_reg_map(self) -> None:
        for physical_reg in self.physical_reg_map:
            for tacreg in self.physical_reg_map[physical_reg]:
                self.tac_reg_map[tacreg] = physical_reg
    
    def update_interference(self, interference:Dict[TacReg, Set[TacReg]]) -> None:
        self.interference_graph = interference
    
    def get_physical_mapping(self, treg:TacReg):
        return self.tac_reg_map[treg] if treg in self.tac_reg_map else None

    def get_used_callee_regs(self) -> list[PReg]:
        return list(self.used_callee_regs)


class ConstantPropogator(object):
    def __init__(self, cfg_func: CFGFunc):
        self.cfg_func = cfg_func
        self.constants:Dict[TacReg, Union[int, str]] = {}
        self.variable_set: set[PReg] = set()
        self.voids:Dict[TacReg, bool] = {}

    def optimize(self) -> None:
        for cfg in self.cfg_func.cfg_blocks:
            self.optimize_block(cfg)

    def add_to_constants(self, tacinst:TacInst) -> None:
        dest = tacinst.get_dest_operand()
        srcs = tacinst.get_src_operands()
        if dest is None or not srcs:
            return

        if isinstance(tacinst, TacLoadImm) and not isinstance(tacinst.imm, TacImmLabel):
            self.constants[dest] = tacinst.imm.val
            return
        elif isinstance(tacinst, TacLoadStr):
            self.constants[dest] = tacinst.string.val
            return
        
        for src in srcs:
            if src not in self.constants:
                return

        if isinstance(tacinst, (TacLoadPrim, TacStorePrim)):
            self.constants[dest] = self.constants[tacinst.src]
            self.variable_set.add(dest)
            pass
        elif isinstance(tacinst, TacBinOp):
            if isinstance(tacinst, TacAdd):
                self.constants[dest] = self.constants[tacinst.src1] + self.constants[tacinst.src2]
            elif isinstance(tacinst, TacSub):
                self.constants[dest] = self.constants[tacinst.src1] - self.constants[tacinst.src2]
            elif isinstance(tacinst, TacMul):
                self.constants[dest] = self.constants[tacinst.src1] * self.constants[tacinst.src2]
            elif isinstance(tacinst, TacDiv):
                self.constants[dest] = int(self.constants[tacinst.src1] / self.constants[tacinst.src2])
        elif isinstance(tacinst, TacIcmp):
            if tacinst.src1 not in self.constants or tacinst.src2 not in self.constants:
                return

            if tacinst.icmp_op == TacCmpOp.EQ:
                self.constants[dest] = 1 if self.constants[tacinst.src1] == self.constants[tacinst.src2] else 0
            elif tacinst.icmp_op == TacCmpOp.NE:
                self.constants[dest] = 1 if self.constants[tacinst.src1] != self.constants[tacinst.src2] else 0
            elif tacinst.icmp_op == TacCmpOp.LT:
                self.constants[dest] = 1 if self.constants[tacinst.src1] < self.constants[tacinst.src2] else 0
            elif tacinst.icmp_op == TacCmpOp.LE:
                self.constants[dest] = 1 if self.constants[tacinst.src1] <= self.constants[tacinst.src2] else 0
        elif isinstance(tacinst, TacUnaryOp):
            if isinstance(tacinst, TacNegate):
                self.constants[dest] = -self.constants[tacinst.src]
            elif isinstance(tacinst, TacNot):
                self.constants[dest] = 1 if self.constants[tacinst.src] == 0 else 0

    def remove_objects_from_constants(self) -> None:
        cpy = self.constants.copy()
        for key in cpy:
            if key in self.variable_set:
                del self.constants[key]

    def optimize_block(self, cfg: CFGBlock) -> bool:
        changed = False
        self.constants.clear()
        for tacinst in cfg.inst_list:
            self.add_to_constants(tacinst)
        
        self.remove_objects_from_constants()
        
        new_inst_list = []
        for i, tacinst in enumerate(cfg.inst_list):
            dest = tacinst.get_dest_operand()
            if dest is None or dest not in self.constants:
                new_inst_list.append(tacinst)
                continue
            
            const_value = self.constants[dest]

            if isinstance(const_value, int):
                new_inst_list.append(TacLoadImm(TacImm(const_value), dest))
            else:
                new_inst_list.append(TacLoadImm(TacStr(const_value), dest))
            changed = True
        
        cfg.inst_list = new_inst_list
        return changed


class DeadCodeEliminator(object):
    def __init__(self, cfg_func: CFGFunc):
        self.cfg_func = cfg_func
        self.constants:Dict[TacReg, Union[int, str]] = {}
        self.variable_set: set[PReg] = set()
        self.voids:Dict[TacReg, bool] = {}

    def optimize(self) -> None:
        for cfg in self.cfg_func.cfg_blocks:
            self.optimize_block(cfg)
        
        while self.cfg_func.calc_liveness():
            for cfg in self.cfg_func.cfg_blocks:
                self.optimize_block(cfg)

    def optimize_block(self, cfg: CFGBlock) -> bool:
        cfg.inst_list[:] = [inst for inst in cfg.inst_list if inst.get_dest_operand() is None or inst.get_dest_operand() in inst.live_out]