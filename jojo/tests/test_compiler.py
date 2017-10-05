from jojo.symbol import scan_symble_list
from jojo.sexp import parse_sexp_list, write_sexp
from jojo.compiler import (
    compile_module,
)
from jojo.vm import (
    VM, RP,
    GET, SET,
    JOJO, MSG, CLO,
    APPLY, IFTE,
    NEW,
    CALL,
)

def test_1():
    code = '''\
    (+jojo six 1 2 add 3 add)
    '''
    sexp_list = parse_sexp_list(scan_symble_list(code))
    module = compile_module('module', sexp_list)
    vm = VM([],
            [RP(module.six)])
    vm = vm.exe()
    assert vm.ds == [6]

import os
import posix

def test_2():
    code = '''\
    (import os)
    (+jojo times os .times)
    '''
    sexp_list = parse_sexp_list(scan_symble_list(code))
    module = compile_module('module', sexp_list)
    vm = VM([],
            [RP(module.times)])
    vm = vm.exe()
    assert type(vm.ds.pop()) == posix.times_result


def test_3():
    code = '''\
    (+jojo t3 1 2 eq? {"true"} {"false"} ifte)
    '''
    sexp_list = parse_sexp_list(scan_symble_list(code))
    module = compile_module('module', sexp_list)
    vm = VM([],
            [RP(module.t3)])
    vm = vm.exe()
    assert vm.ds == ["false"]
