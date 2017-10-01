import inspect
import types

from jojo.vm import (
    VM, RP,
    GET, SET,
    JOJO, MSG, CLO,
    APPLY, IFTE,
    NEW,
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

def test_1():
    jojo = JOJO(
        "xieyuheng", Human, NEW, SET("h"),
        "kkk took my baby away", GET("h"), MSG("say"),
        GET("h"), MSG("name"),
    )
    vm = VM([],
            [RP(JOJO(jojo))]
    )
    vm = vm.exe()
    assert vm.ds == ["xieyuheng"]


def test_2():
    jojo = JOJO(
        5, SET("1"),
        100,
        [SET("2"), GET("2"), GET("2"), add, GET("1"), add],
        CLO,
        APPLY
    )
    vm = VM([],
            [RP(JOJO(jojo))]
    )
    vm = vm.exe()
    assert vm.ds == [205]


def test_3():
    jojo = JOJO(
        False,
        ["true"], CLO,
        ["false"], CLO,
        IFTE
    )
    vm = VM([],
            [RP(JOJO(jojo))]
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
    jojo = JOJO(
        "aaa",
        "bbb",
        ["k1", "k2", "k3"],
        {"1": "k1", "2": "k2", "3": "k3"},
        k,
    )
    vm = VM([],
            [RP(JOJO(jojo))]
    )
    vm = vm.exe()
    ds1 = [[
        'aaa',
        'bbb',
        ('k1', 'k2', 'k3'),
        'default k0',
        {'1': 'k1', '2': 'k2', '3': 'k3'}
    ]]
    assert vm.ds == ds1
