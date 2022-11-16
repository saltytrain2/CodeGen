from __future__ import annotations
from tacnodes import *
from collections import deque
from typing import Deque
from heapq import heappush, heappop


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
        self.live_out = self.live_out.union(*[i.get_live_out() for i in self.succs])
        succ_live = self.live_out
        for inst in reversed(self.inst_list):
            nodechanged = inst.update_live_set(succ_live)
            if not changed:
                changed = nodechanged
            succ_live = inst.get_live_set()

        return changed

    def fixed_alloc(self, reg_allocator:FixedRegisterAllocator) -> int:
        """ 
        We now assign each tacreg a physical register based on the instruction
        This is heavily based on a lot of assumptions on what our tac looks like
        We know from our tac that no more than two registers will be alive at the same time,
        allowing us very easily determine register allocation

        Some special registers will always be allocated for certain needs, which are shown below

        r11 -> trash register for arithmetic operations
        r10 -> temporary register for immediates (we wont be using more than per instruction)
        rcx -> immediate register
        rax -> subroutine return register
        rbp + offset -> stack temporaries
        """
        offset = 0
        regs_to_alloc:List[TacReg] = []
        # before we just start allocating registers, we fix all returns that are supposed to be fixed
        for inst in self.inst_list:
            if isinstance(inst, TacAlloc):
                inst.dest.set_preg(PReg("%rbp", offset))
                offset -= 8
            elif isinstance(inst, (TacCreate, TacCall, TacSyscall)):
                # TODO this might need to change
                inst.dest.set_preg(PReg("%rax"))
            elif isinstance(inst, TacRet):
                pass
            elif isinstance(inst, TacLoadImm):
                inst.dest.set_preg(PReg("%r10"))
            elif isinstance(inst, (TacBinOp, TacUnaryOp, TacLoad)):
                regs_to_alloc.append(inst.dest)

        
        for treg in regs_to_alloc:
            physical_reg = reg_allocator.get_unused_reg(treg)
            assert physical_reg is not None

            treg.set_preg(physical_reg)

        return abs(offset)


class FixedRegisterAllocator(object):
    def __init__(self, interference_graph:Dict[TacReg, Set[TacReg]]=None):
        self.return_reg:PReg = PReg("%rax")
        self.caller_saved:List[PReg] = [
            PReg("%rdi"), PReg("%rsi"), PReg("%rdx"), PReg("%rcx"), PReg("%r8"), PReg("%r9")
        ]
        self.callee_saved:List[PReg] = [
            PReg("%rbx"), PReg("%r12"), PReg("%r13"), PReg("%r14"), PReg("%r15")
        ]
        self.interference_graph = interference_graph if interference_graph is not None else defaultdict(set)
        self.physical_reg_map:Dict[PReg, List[TacReg]] = defaultdict(list)
        self.tac_reg_map:Dict[PReg, List[TacReg]] = defaultdict(list)
        self.reset()

    def get_caller_reg(self, input_reg:TacReg) -> TacReg:
        for physical_reg in self.caller_saved:
            # if the register is unused, yay
            if not self.physical_reg_map[physical_reg]:
                self.physical_reg_map[physical_reg].append(input_reg)
                return physical_reg
            
            for tac_reg in self.physical_reg_map[physical_reg]:
                # we can reuse the register since they do not overlap
                if tac_reg not in self.interference_graph[input_reg]:
                    self.physical_reg_map[physical_reg].append(input_reg)
                    return physical_reg

        # we fell through, we found nothing
        return None

    def get_callee_reg(self, input_reg:TacReg) -> TacReg:
        for physical_reg in self.callee_saved:
            # if the register is unused, yay
            if not self.physical_reg_map[physical_reg]:
                self.physical_reg_map[physical_reg].append(input_reg)
                return physical_reg
            
            for tac_reg in self.physical_reg_map[physical_reg]:
                # we can reuse the register since they do not overlap
                if tac_reg not in self.interference_graph[input_reg]:
                    self.physical_reg_map[physical_reg].append(input_reg)
                    return physical_reg
        # we fell through, we found nothing
        return None
    
    def get_caller_regs(self) -> Set[PReg]:
        return self.caller_saved

    def get_callee_regs(self) -> Set[PReg]:
        return self.callee_saved

    def add_used_reg(self, physical_reg:PReg, treg:TacReg) -> None:
        self.physical_reg_map[physical_reg].append(treg)
    
    def get_unused_reg(self, tacreg:TacReg) -> None:
        # lets try to get a caller-saved register
        reg = self.get_caller_reg(tacreg)
        if reg is not None:
            return reg

        # try to get a callee-saved register instead
        reg = self.get_callee_reg(tacreg)
        return reg

    def reset(self) -> None:
        self.physical_reg_map.clear()
        self.tac_reg_map.clear()
    
    def update_interference(self, interference:Dict[TacReg, Set[TacReg]]) -> None:
        self.interference_graph = interference


class CFGFunc(object):
    def __init__(self, func:TacFunc):
        self.name = func.name
        self.params = func.params
        self.stack_space = 0
        self.cfg_map:Dict[str, CFGBlock] = defaultdict(CFGBlock, name="")
        self.cfg_blocks:List[CFGBlock] = []
        self.interference:Dict[TacReg, Set[TacReg]] = defaultdict(set)
        self.reg_allocator:FixedRegisterAllocator = FixedRegisterAllocator({})
        self.process_func(func)
    
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
                cfg_block.add_succ(self.cfg_map[str(label.num)])
                self.cfg_map[str(label.num)].add_pred(cfg_block)

    def get_cfg_blocks(self) -> List[CFGBlock]:
        return self.cfg_blocks

    def __repr__(self) -> str:
        str_list = [f"{self.name}{str(self.params)} {self.stack_space}\n"]
        for cfg_block in self.cfg_blocks:
            str_list.append(repr(cfg_block))
        return "".join(str_list)
    
    def calc_liveness(self) -> None:
        for cfg_block in self.cfg_blocks:
            cfg_block.calc_liveness()
    
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
                cfg_block.dominators = {cfg_block}.union(set.intersection(*[pred.dominators for pred in cfg_block.preds]))
                changed = True if prev_dominators != cfg_block.dominators else changed

    def alloc_regs(self) -> None:
        self.fixed_alloc()
    
    def fixed_alloc(self) -> None:
        """  
        This is the register allocation scheme that is solely for PA5
        We hardcode all register allocations, which is allowed since we spill every temp to memory
        """
        # update the interference graph
        self.reg_allocator.update_interference(self.interference)

        # first handle the parameters
        offset = 8
        param_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
        for i, param in enumerate(self.params):
            if i < 7:
                param.set_preg(PReg(param_regs[i]))
            else:
                param.set_preg(PReg("%rbp", offset))
                offset += 8
        
        self.stack_space += offset - 8

        # now handle everything else
        for cfg_block in self.cfg_blocks:
            stack_space = cfg_block.fixed_alloc(self.reg_allocator)
            self.stack_space += stack_space
        pass

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
        work_list:Deque[CFGBlock] = deque()
        work_list.append(self.cfg_blocks[-1])
        while work_list:
            cfg_block = work_list.popleft()
            changed = cfg_block.calc_liveness()

            if changed:
                for pred in cfg_block.preds:
                    work_list.append(pred)

        # through these live sets, generate the resulting interference graph
        for cfg_block in self.cfg_blocks:
            for inst in cfg_block.inst_list:
                live_regs = inst.get_live_set()
                for reg in live_regs:
                    self.interference[reg].update(live_regs)
                    self.interference[reg].remove(reg)
                pass
        pass

    def print_interference(self) -> None:
        for reg, reg_set in self.interference.items():
            print(f"{reg}: {reg_set if reg_set else ''}")
        pass

    def linear_scan_alloc(self) -> None:
        def expire_old_intervals(active:List[int], start:int):
            while active[0] > start:
                heappop(active)
            self.reg_allocator.dealloc_reg()

        def spill_at_interval():
            pass
        pass
        #for inst in self.
    
    def to_tacfunc(self) -> TacFunc:
        insts = []
        for cfg_block in self.cfg_blocks:
            insts.extend(cfg_block.inst_list)

        return TacFunc(self.name, self.params, insts, self.stack_space)

