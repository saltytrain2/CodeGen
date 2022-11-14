from __future__ import annotations
from tacnodes import *
from collections import deque
from typing import Deque
import networkx as nx


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



class CFGFunc(object):
    def __init__(self, func:TacFunc):
        self.name = func.name
        self.params = func.params
        self.cfg_map:Dict[str, CFGBlock] = defaultdict(CFGBlock, name="")
        self.cfg_blocks:List[CFGBlock] = []
        self.interference:Dict[TacReg, Set[TacReg]] = defaultdict(set)
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
        str_list = [f"{self.name}{str(self.params)}\n"]
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
        used_regs:Dict[PReg, TacReg] = defaultdict(TacReg, num=-1)
        visited_blocks:Set[CFGBlock] = set()
        work_list:Deque[CFGBlock] = deque()
        work_list.append(self.cfg_map["entry"])

        while work_list:
            cur_block = work_list.popleft()
            visited_blocks.add(cur_block)
            pass

    def precolor_regs(self) -> None:
        # some registers are forced due to the calling convention
        offset = 0
        for cfg_block in self.cfg_blocks:
            for inst in cfg_block.inst_list:
                # call instructions always return values in rax/eax
                if isinstance(inst, (TacCreate, TacCall, TacSyscall)):
                    inst.dest.set_preg(PReg("rax"))
                
                # declared variables on stack will always be stored in rbp - offset
                if isinstance(inst, TacDeclare):
                    inst.dest.set_preg(PReg("rbp", offset))
                    offset -= 8
            pass
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
