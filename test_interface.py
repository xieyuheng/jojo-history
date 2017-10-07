import jojo

def test_1():
    m = jojo.load("docs/examples/square.jo")
    ds = jojo.run([4],
                  [m.square])
    assert ds == [16]
