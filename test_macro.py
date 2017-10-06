import jojo

def test_1():
    code = '''\
    (+jojo c :x!
      (cond
        [:x 1 eq?] "one"
        [:x 2 eq?] "two"
        else ["big"]))
    (+jojo t 1 c 2 c 3 c)
    '''
    sexp_vect = jojo.parse_sexp_vect(jojo.scan_string_vect(code))
    module = jojo.compile_module('module', sexp_vect)
    vm = jojo.VM([],
            [jojo.RP(module.t)])
    vm = vm.exe()
    assert vm.ds == ["one", "two", "big"]


def test_2():
    m = jojo.create_module("module1", "docs/examples/cond.jo")
    print (dir(m))
    vm = jojo.VM([],
                 [jojo.RP(getattr(m, "a-length"))])
    vm = vm.exe()
    assert vm.ds == [4]
