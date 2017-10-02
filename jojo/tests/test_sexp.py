from jojo.symbol import scan_symble_list
from jojo.sexp import parse_sexp_list, write_sexp

string = '''\
(1 (1 2 3) 2 (1 2 3) 3 "123")
(1 (1 2 3) 2 (1 2 3) 3 "123")
(1 (1 2 3) 2 (1 2 3) 3 "123")
'''
def newline():
    print("")

def test_0():
    symbol_list = scan_symble_list(string)
    sexp_list = parse_sexp_list(symbol_list)
    for sexp in sexp_list:
        write_sexp(sexp)
        newline()

test_0()
