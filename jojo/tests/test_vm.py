import inspect
import types

from jojo.vm import (
    VM, RP,
    GET, SET,
    JOJO, MSG, CLO,
    APPLY, IFTE,
    NEW,
    CALL,
)

def drop(a):
    return ()

def dup(a):
    return (a, a)

def over(a, b):
    return (a, b, a)

def tuck(a, b):
    return (b, a, b)

def swap(a, b):
    return (b, a)

def add(a, b):
    return a + b

def test_0():
    vm = VM(
        [1, 2],
        [RP(JOJO(add, 3, add,
                 1, 2, swap, dup, dup, drop))]
    )
    vm = vm.exe()
    assert vm.ds == [6, 2, 1, 1]


class Human:
    def __init__(self, name):
        self.name = name
    def say(self, msg):
        print ("{name}: {message}"
               .format(name=self.name,
                       message=msg))
    def sing(self):
        return 'singing'


jojo_1 = JOJO(
    "xieyuheng", Human, NEW, SET("h"),
    "kkk took my baby away", GET("h"), MSG("say"),
    GET("h"), MSG("name"),
)

def test_1():
    vm = VM([],
            [RP(jojo_1)])
    vm = vm.exe()
    assert vm.ds == ["xieyuheng"]

jojo_2 = JOJO(
    5, SET("1"),
    100,
    [SET("2"), GET("2"), GET("2"), add, GET("1"), add],
    CLO,
    APPLY
)

def test_2():
    vm = VM([],
            [RP(jojo_2)])
    vm = vm.exe()
    assert vm.ds == [205]

jojo_3 = JOJO(
    False,
    ["true"], CLO,
    ["false"], CLO,
    IFTE,
)

def test_3():
    vm = VM([],
            [RP(jojo_3)]
    )
    vm = vm.exe()
    assert vm.ds == ["false"]


def test_4():
    def k(a, b = "b0", *arg_list, k0 = "default k0", **arg_dict):
        return [
            a,
            b,
            arg_list,
            k0,
            arg_dict,
        ]
    jojo_4 = JOJO(
        "aaa",
        "bbb",
        ["k1", "k2", "k3"],
        {"1": "k1", "2": "k2", "3": "k3"},
        k,
    )
    vm = VM([],
            [RP((jojo_4))])
    vm = vm.exe()
    ds1 = [[
        'aaa',
        'bbb',
        ('k1', 'k2', 'k3'),
        'default k0',
        {'1': 'k1', '2': 'k2', '3': 'k3'}
    ]]
    assert vm.ds == ds1


import sys

k_5 = 5
j_5 = JOJO(
    CALL(sys.modules[__name__], 'add'),
)

jojo_5 = JOJO(
    CALL(sys.modules[__name__], 'k_5'),
    CALL(sys.modules[__name__], 'k_5'),
    CALL(sys.modules[__name__], 'add'),
    CALL(sys.modules[__name__], 'dup'),
    CALL(sys.modules[__name__], 'j_5'),
)

def test_5():
    vm = VM([],
            [RP((jojo_5))])
    vm = vm.exe()
    assert vm.ds == [20]
