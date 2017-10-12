from jojo import scan_string_vect


def test_0():
    assert scan_string_vect('123 123')   == ['123', '123']
    assert scan_string_vect('123 "123"') == ['123', '"123"']
    assert scan_string_vect('123"123"')  == ['123', '"123"']
    assert scan_string_vect('123" 123"') == ['123', '" 123"']


def test_1():
    assert scan_string_vect('(1 (2) 3)') == ['(', '1', '(', '2', ')', '3', ')']
