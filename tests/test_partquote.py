import jojo

def test_1():
    code = '''\
    (+jojo c :x!
      `(a (@ :x :x mul) b (@ :x :x mul) c))
    (+jojo t 4 c list->vect vect-spread)
    '''
    sexp_vect = jojo.parse_sexp_vect(jojo.code_scan(code))
    module = jojo.compile_module('module', sexp_vect)
    vm = jojo.VM([],
                 [jojo.RP(module.t)])
    vm = vm.exe()
    assert vm.ds == ["a", 16, "b", 16, "c"]


def test_2():
    code = '''\
    (+jojo c :x!
      `(a (@ :x :x mul) b (@ :x :x mul) c))
    (+jojo t 4 c list-spread)
    '''
    sexp_vect = jojo.parse_sexp_vect(jojo.code_scan(code))
    module = jojo.compile_module('module', sexp_vect)
    vm = jojo.VM([],
                 [jojo.RP(module.t)])
    vm = vm.exe()
    assert vm.ds == ["a", 16, "b", 16, "c"]
