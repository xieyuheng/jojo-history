from jojo.symbol import scan_symble_list


def test_0():
    assert scan_symble_list('123 123')   == ['123', '123']
    assert scan_symble_list('123 "123"') == ['123', '"123"']
    assert scan_symble_list('123"123"')  == ['123', '"123"']
    assert scan_symble_list('123" 123"') == ['123', '" 123"']


def test_1():
    assert scan_symble_list('(1 (2) 3)') == ['(', '1', '(', '2', ')', '3', ')']
