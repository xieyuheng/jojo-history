from jojo import code_scan, parse_sexp_vect, sexp_print

string = '''\
(1 (1 2 3) 2 (1 2 3) 3 "123")
(1 (1 2 3) 2 (1 2 3) 3 "123")
(1 (1 2 3) 2 (1 2 3) 3 "123")
'a
'(1 2 3)
('a 'b '(1 2 3))
'''
def newline():
    print("")

def test_0():
    symbol_vect = code_scan(string)
    sexp_vect = parse_sexp_vect(symbol_vect)
    for sexp in sexp_vect:
        sexp_print(sexp)
        newline()

test_0()
