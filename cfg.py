from __future__ import annotations
from cfgnodes import *

class CFG(object):
    def __init__(self, tacfuncs:List[TacFunc]):
        self.cfg_list:List[CFGFunc] = []
        self.process_tacfuncs(tacfuncs)
    
    def process_tacfuncs(self, tacfuncs:List[TacFunc]) -> None:
        for tacfunc in tacfuncs:
            self.cfg_list.append(CFGFunc(tacfunc))

    def get_cfg_funcs(self) -> List[CFGFunc]:
        return self.cfg_list

    def debug_cfg(self) -> None:
        for cfg_func in self.cfg_list:
            print(repr(cfg_func))
    
    def optimize(self) -> None:
        pass
    
    def set_dominators(self) -> None:
        for cfg in self.cfg_list:
            cfg.set_dominators()

    def build_interference_graph(self) -> None:
        # find the live ranges of each variable
        # for cfg in self.cfg_list:
        #     cfg.calc_liveness()
        pass