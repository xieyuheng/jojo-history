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
