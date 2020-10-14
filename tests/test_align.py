from kaldialign import align, edit_distance

EPS = '*'


def test_align():
    a = ['a', 'b', 'c']
    b = ['a', 's', 'x', 'c']
    ali = align(a, b, EPS)
    assert ali == [('a', 'a'), (EPS, 's'), ('b', 'x'), ('c', 'c')]


def test_edit_distance():
    a = ['a', 'b', 'c']
    b = ['a', 's', 'x', 'c']
    results = edit_distance(a, b)
    assert results == {
        'ins': 1,
        'del': 0,
        'sub': 1,
        'total': 2
    }
