import jojo

def test_1():
    code = '''\
    (+jojo c
      (list 1 2 add dup))
    (+jojo t
      c list->vect vect-spread)
    '''
    sexp_vect = jojo.parse_sexp_vect(jojo.code_scan(code))
    module = jojo.compile_module(__name__ + 'test_1', sexp_vect)
    vm = jojo.VM([],
                 [jojo.RP(module.t)])
    vm = vm.exe()
    assert vm.ds == [3, 3]


def test_2():
    code = '''\
    (+jojo c
      (vect 1 2 add dup))
    (+jojo t
      c vect-spread)
    '''
    sexp_vect = jojo.parse_sexp_vect(jojo.code_scan(code))
    module = jojo.compile_module(__name__ + 'test_2', sexp_vect)
    vm = jojo.VM([],
                 [jojo.RP(module.t)])
    vm = vm.exe()
    assert vm.ds == [3, 3]
