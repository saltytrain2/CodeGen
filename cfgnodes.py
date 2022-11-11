from __future__ import annotations
from tacnodes import *


class CFGBlock(object):
    def __init__(self, name:str):
        self.name = name
        self.preds:List[CFGBlock] = []
        self.succs:List[CFGBlock] = []
        self.live_in:Set[TacReg] = set()
        self.live_out:Set[TacReg] = set()
        self.inst_list:List[TacValue] = []
    
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
        raise Exception("last instructions is not a terminator")
    
    def __repr__(self) -> str:
        str_list = [f"Preds: {[i.name for i in self.preds]}\n", f"Succs: {[i.name for i in self.succs]}\n"]
        for inst in self.inst_list:
            str_list.append(repr(inst))
        
        return "".join(str_list)


class CFG(object):
    def __init__(self, func:TacFunc):
        self.name = func.name
        self.cfg_map:Dict[str, CFGBlock] = defaultdict(CFGBlock, name="")
        self.cfg_list:List[CFGBlock] = []
        self.process_func(func)
    
    def process_func(self, func:TacFunc) -> None:
        # allocate all CFB Blocks
        cur_block = CFGBlock("entry")
        self.cfg_map["entry"] = cur_block
        self.cfg_list.append(cur_block)

        # first pass is to get all the blocks
        for inst in func.insts:
            if isinstance(inst, TacLabel):
                label_num = str(inst.num)
                cur_block = CFGBlock(label_num)
                self.cfg_map[label_num] = cur_block
                self.cfg_list.append(cur_block)
            cur_block.add_inst(inst)
        
        # second pass to establish correct linkage between blocks
        for cfg in self.cfg_list:
            branch_labels = cfg.get_branch_labels()

            for label in branch_labels:
                cfg.add_succ(self.cfg_map[str(label.num)])
                self.cfg_map[str(label.num)].add_pred(cfg)


    def get_cfg_blocks(self) -> List[CFGBlock]:
        return self.cfg_list
    
    def debug_cfg(self) -> None:
        print(self.name)
        for cfg in self.cfg_list:
            print(repr(cfg))
