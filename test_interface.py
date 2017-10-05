import jojo

def test_1():
    m = jojo.create_module("module1", "docs/examples/square.jo")
    vm = jojo.VM([4],
                 [jojo.RP(m.square)])
    vm = vm.exe()
    assert vm.ds == [16]
