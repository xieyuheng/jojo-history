import jojo

def test_1():
    m = jojo.create_module("module1", "docs/examples/cond.jo")
    print (dir(m))
    vm = jojo.VM([],
                 [jojo.RP(getattr(m, "a-length"))])
    vm = vm.exe()
    assert vm.ds == [4]
