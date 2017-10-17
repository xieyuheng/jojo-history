from jojo import code_scan


def test_0():
    assert code_scan('123 123')   == ['123', '123']
    assert code_scan('123 "123"') == ['123', '"123"']
    assert code_scan('123"123"')  == ['123', '"123"']
    assert code_scan('123" 123"') == ['123', '" 123"']


def test_1():
    assert code_scan('(1 (2) 3)') == ['(', '1', '(', '2', ')', '3', ')']
