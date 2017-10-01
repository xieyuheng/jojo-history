from jojo import symbol


def test_0():
    assert symbol.scan('123 123')   == ['123', '123']
    assert symbol.scan('123 "123"') == ['123', '"123"']
    assert symbol.scan('123"123"')  == ['123', '"123"']
    assert symbol.scan('123" 123"') == ['123', '" 123"']


def test_1():
    assert symbol.scan('(1 (2) 3)') == ['(', '1', '(', '2', ')', '3', ')']
