from collections import defaultdict
from deserialize import *
from coolast import *
from tac import *
from maps import *
import sys


def main(argv):
    cl_type_file = argv[1]
    with open(cl_type_file, 'r') as file:
        ast_lines = [line.rstrip("\n\r") for line in reversed(file.readlines())]

    class_map, impl_map, parent_map, class_list = read_ast(ast_lines)
    tac = Tac(class_map, impl_map, parent_map, class_list)
    tac.tacgen()
    tac.debug_tac()

if __name__ == '__main__':
    main(sys.argv)