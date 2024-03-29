from __future__ import annotations
from tacnodes import *
from collections import deque, defaultdict
from typing import Deque
from heapq import heappush, heappop
from optimizations import FixedRegisterAllocator, ConstantPropogator


class CFGBlock(object):
    def __init__(self, name:str):
        self.name = name
        self.preds:List[CFGBlock] = []
        self.succs:List[CFGBlock] = []
        self.live_out:Set[TacReg] = set()
        self.live_in:Set[TacReg] = set()
        self.dominators:Set[CFGBlock] = set()
        self.inst_list:List[TacInst] = []
    
    def add_inst(self, inst:TacInst):
        self.inst_list.append(inst)

    def add_pred(self, pred:CFGBlock):
        self.preds.append(pred)
    
    def add_succ(self, succ:CFGBlock):
        self.succs.append(succ)
    
    def get_branch_labels(self) -> List[TacLabel]:
        last_inst = self.inst_list[-1]
        if isinstance(last_inst, TacBr):
            return last_inst.get_branch_targets()
        elif isinstance(last_inst, (TacRet, TacUnreachable)):
            return []

        # error case
        raise Exception("last instruction is not a terminator")
    
    def get_live_in(self) -> Set[TacReg]:
        return self.live_in

    def get_live_out(self) -> Set[TacReg]:
        return self.live_out
    
    def __repr__(self) -> str:
        str_list = [
            f"Preds: {[i.name for i in self.preds]}\n", 
            f"Succs: {[i.name for i in self.succs]}\n",
            f"Dominators: {[i.name for i in list(self.dominators)]}\n"
        ]
        for inst in self.inst_list:
            str_list.append(repr(inst))
        
        return "".join(str_list) + "\n"
    
    def calc_liveness(self, out_set=None) -> bool:
        changed = False
        self.live_out = self.live_out.union(*[i.get_live_in() for i in self.succs])
        succ_live_in = self.live_out
        for inst in reversed(self.inst_list):
            nodechanged = inst.update_live_set(succ_live_in)
            if nodechanged:
                changed = nodechanged
            succ_live_in = inst.get_live_in()
        
        self.live_in = self.inst_list[0].get_live_in()
        return changed

    def fixed_alloc(self, reg_allocator:FixedRegisterAllocator) -> int:
        """ 
        We now assign each tacreg a physical register based on the instruction
        This is heavily based on a lot of assumptions on what our tac looks like

        Some special registers will always be allocated for certain needs, which are shown below

        rdi -> self pointer
        rax -> subroutine return register and dynamic dispatch calling register
        rbp + offset -> stack temporaries

        """
        offset = -8
        regs_to_alloc:List[TacReg] = []
        # before we just start allocating registers, we fix all returns that are supposed to be fixed
        for inst in self.inst_list:
            if isinstance(inst, TacAlloc):
                inst.dest.set_preg(PReg("%rbp", offset))
                offset -= 8
            elif isinstance(inst, TacStoreSelf):
                inst.dest.set_preg(PReg("%r12"))
                reg_allocator.add_used_reg(PReg("%r12"), inst.dest)
            elif isinstance(inst, (TacCreate, TacCall, TacSyscall, TacBinOp, TacUnaryOp, TacLoad, TacLoadPrim, TacLoadImm)):
                regs_to_alloc.append(inst.dest)

        
        for treg in regs_to_alloc:
            physical_reg = reg_allocator.get_unused_reg(treg)
            #assert physical_reg is not None

            treg.set_preg(physical_reg)

        return abs(offset + 8)

    def resolve_stack_discipline(self, reg_allocator:FixedRegisterAllocator):
        for inst in self.inst_list:
            if not isinstance(inst, (TacCall, TacSyscall, TacCreate)):
                continue

            # we want to find all live variables and mark variables that reside in caller-saved registers
            live_regs:List[PReg] = [
                reg_allocator.get_physical_mapping(i) for i in inst.get_live_out() if reg_allocator.get_physical_mapping(i) is not None and i != inst.dest
            ]
            live_volatile_regs:List[PReg] = [i for i in live_regs if i in reg_allocator.get_caller_regs()]
            inst.save_regs = live_volatile_regs
        pass


class CFGFunc(object):
    def __init__(self, func:TacFunc):
        self.name = func.name
        self.params = func.params
        self.stack_space = 0
        self.cfg_map:Dict[str, CFGBlock] = defaultdict(CFGBlock, name="")
        self.cfg_blocks:List[CFGBlock] = []
        self.interference:Dict[TacReg, Set[TacReg]] = defaultdict(set)
        self.reg_allocator:FixedRegisterAllocator = FixedRegisterAllocator()
        self.process_func(func)
        self.self_reg = func.self_reg
        self.num = func.num
        self.callee_saved: list[PReg] = []
        self.self_reg.set_preg(PReg("%r12"))
        self.reg_allocator.add_used_reg(PReg("%r12"), self.self_reg)
    
    def process_func(self, func:TacFunc) -> None:
        # allocate all CFB Blocks
        cur_block = CFGBlock("entry")
        self.cfg_map["entry"] = cur_block
        self.cfg_blocks.append(cur_block)

        # first pass is to get all the blocks
        for inst in func.insts:
            if isinstance(inst, TacLabel):
                label_num = str(inst.num)
                cur_block = CFGBlock(label_num)
                self.cfg_map[label_num] = cur_block
                self.cfg_blocks.append(cur_block)
            cur_block.add_inst(inst)
        
        # second pass to establish correct linkage between blocks
        for cfg_block in self.cfg_blocks:
            branch_labels = cfg_block.get_branch_labels()

            for label in branch_labels:
                if str(label.num) in self.cfg_map:
                    cfg_block.add_succ(self.cfg_map[str(label.num)])
                    self.cfg_map[str(label.num)].add_pred(cfg_block)

    def get_cfg_blocks(self) -> List[CFGBlock]:
        return self.cfg_blocks

    def __repr__(self) -> str:
        str_list = [f"{self.name}{str(self.params)} {self.stack_space}\n"]
        for cfg_block in self.cfg_blocks:
            str_list.append(repr(cfg_block))
        return "".join(str_list)

    def create_reg(self, isstack: bool=False) -> TacReg:
        temp = TacReg(self.num, isstack)
        self.num += 1
        return temp

    def create_label(self) -> TacLabel:
        temp = TacLabel(self.num)
        self.num += 1
        return temp
    
    def calc_liveness(self) -> bool:
        for cfg_block in self.cfg_blocks:
            cfg_block.live_out.clear()
            cfg_block.live_in.clear()

        # make sure self is set as a global variable: must always persist
        #self.cfg_blocks[-1].live_out.add(self.self_reg)
        work_list:Deque[CFGBlock] = deque([i for i in reversed(self.cfg_blocks)])
        self.cfg_blocks[-1].live_out.add(self.self_reg)
        while work_list:
            cfg_block = work_list.popleft()
            changed = cfg_block.calc_liveness()

            if changed:
                for pred in cfg_block.preds:
                    work_list.append(pred)
        
        return changed
        # for cfg_block in reversed(self.cfg_blocks):
        #     cfg_block.calc_liveness()
    
    def set_dominators(self) -> None:
        # set the dominator of the entry block
        self.cfg_map["entry"].dominators.add(self.cfg_map["entry"])
        for cfg_block in self.cfg_blocks[1:]:
            cfg_block.dominators = set(self.cfg_blocks)

        changed = True
        while changed:
            changed = False
            for cfg_block in self.cfg_blocks[1:]:
                prev_dominators = cfg_block.dominators.copy()
                dominators = [pred.dominators for pred in cfg_block.preds]
                if dominators:
                    cfg_block.dominators = {cfg_block}.union(set.intersection(*dominators if dominators != [] else set()))
                changed = True if prev_dominators != cfg_block.dominators else changed

    def alloc_regs(self) -> None:
        self.fixed_alloc()
    
    def fixed_alloc(self) -> None:
        """  
        This is the register allocation scheme that is solely for PA5
        We spill all declared variables to memory, leaving only temporaries inside registers
        Although this results in incorrect code for lots of temporaries, it simplifies the register allocation scheme significantly
        The PA6 implementation will correctly spill temporaries to memory when all the registers are filled
        """
        # update the interference graph
        self.reg_allocator.update_interference(self.interference)

        # first handle the parameters
        offset = 16
        param_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
        for i, param in enumerate(self.params):
            if i < 7:
                param.set_preg(PReg(param_regs[i]))
            else:
                param.set_preg(PReg("%rbp", offset))
                offset += 8
        
        self.stack_space += offset - 16

        # now handle everything else
        for cfg_block in self.cfg_blocks:
            stack_space = cfg_block.fixed_alloc(self.reg_allocator)
            self.stack_space += stack_space
        
        # create a mapping of physical registers to actual registers
        self.reg_allocator.construct_tac_reg_map()
        self.callee_saved = self.reg_allocator.get_used_callee_regs()

    def precolor_regs(self) -> None:
        # some registers are forced due to the calling convention
        offset = 0
        param_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
        for i, param in enumerate(self.params):
            if i < 7:
                param.set_preg(PReg(param_regs[i]))
            else:
                param.set_preg(PReg("%rbp", offset))
                offset += 8

        offset = 8
        for inst in self.cfg_blocks[-1].inst_list:
            # declared variables on stack will always be stored in rbp - offset
            if not isinstance(inst, TacDeclare):
                break
            inst.dest.set_preg(PReg("%rbp", offset))
            offset -= 8
        pass

    def calc_interference(self) -> None:
        # generate live sets for each node in CFG
        work_list:Deque[CFGBlock] = deque([i for i in reversed(self.cfg_blocks)])
        self.cfg_blocks[-1].live_out.add(self.self_reg)
        while work_list:
            cfg_block = work_list.popleft()
            changed = cfg_block.calc_liveness()

            if changed:
                for pred in cfg_block.preds:
                    work_list.append(pred)

        # through these live sets, generate the resulting interference graph
        for cfg_block in self.cfg_blocks:
            for inst in cfg_block.inst_list:
                live_regs = inst.get_live_out()
                for reg in live_regs:
                    self.interference[reg].update(live_regs)
                pass
            for reg in self.interference:
                if reg in self.interference[reg]:
                    self.interference[reg].remove(reg)
        pass

    def print_interference(self) -> None:
        for reg, reg_set in self.interference.items():
            print(f"{reg}: {reg_set if reg_set else ''}")
        pass
    
    def to_tacfunc(self) -> TacFunc:
        insts = []
        for cfg_block in self.cfg_blocks:
            insts.extend(cfg_block.inst_list)

        # align the stack properly
        if self.stack_space % 16 != 0:
            self.stack_space += 8

        return TacFunc(self.name, self.params, insts, self.stack_space, self.callee_saved)

    def resolve_stack_discipline(self) -> None:
        # we want to make sure we are able to push/pop necessary registers when calling functions
        for cfg_block in self.cfg_blocks:
            cfg_block.resolve_stack_discipline(self.reg_allocator)
