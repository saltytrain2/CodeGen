from __future__ import annotations
from tacnodes import *


class CFGBlock(object):
    def __init__(self, name:str):
        self.name = name
        self.preds:List[CFGBlock] = []
        self.succs:List[CFGBlock] = []
        self.liveness:List[Set[TacReg]] = []
        self.live_out:Set[TacReg] = set()
        self.live_in:Set[TacReg] = set()
        self.kill:set[TacReg] = set()
        self.gen:Set[TacReg] = set()
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
        elif isinstance(last_inst, TacRet):
            return []
        # error case
        raise Exception("last instruction is not a terminator")
    
    def __repr__(self) -> str:
        str_list = [
            f"Preds: {[i.name for i in self.preds]}\n", 
            f"Succs: {[i.name for i in self.succs]}\n",
            f"Dominators: {[i.name for i in list(self.dominators)]}\n"
        ]
        for inst in self.inst_list:
            str_list.append(repr(inst))
        
        return "".join(str_list)
    
    def calc_liveness(self, out_set=None) -> bool:
        changed = False
        max_index = len(self.inst_list) - 1
        if out_set is None:
            out_set = set()
        self.live_out = out_set.copy()
        live_sets = [out_set.copy()]

        for i, inst in enumerate(reversed(self.inst_list[:])):
            dead_reg = inst.get_dead_reg()
            # we know that since this is SSA, encountering an assignment to a register
            # that has not been used must be dead code
            if dead_reg is not None and dead_reg not in out_set:
                self.inst_list.remove(inst)
                continue
            
            live_regs = inst.get_live_regs()
            out_set = out_set.update(live_regs)
            live_sets.append(out_set.copy())

            if out_set != self.liveness[max_index - i]:
                changed = True
        
        self.liveness = live_sets
        return changed


class CFGFunc(object):
    def __init__(self, func:TacFunc):
        self.name = func.name
        self.params = func.params
        self.cfg_map:Dict[str, CFGBlock] = defaultdict(CFGBlock, name="")
        self.cfg_blocks:List[CFGBlock] = []
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
                if prev_dominators != cfg_block.dominators:
                    changed = True

