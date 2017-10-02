from jojo.symbol import scan_symble_list
from jojo.sexp import parse_sexp_list, write_sexp
from jojo.compiler import (
    compile_module
)
from jojo.vm import (
    VM, RP,
    GET, SET,
    JOJO, MSG, CLO,
    APPLY, IFTE,
    NEW,
    CALL,
)

code_1 = '''\
(import sys)
(+jojo six ><><><)
'''

def test_1():
    sexp_list = parse_sexp_list(scan_symble_list(code_1))
    module_1 = compile_module('module_1', sexp_list)
    vm = VM([],
            [RP((module_1.six))])
    vm = vm.exe()
    assert vm.ds == [6]
