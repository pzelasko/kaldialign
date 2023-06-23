from kaldialign import align, edit_distance

EPS = '*'


def test_align():
    a = ['a', 'b', 'c']
    b = ['a', 's', 'x', 'c']
    ali = align(a, b, EPS)
    assert ali == [('a', 'a'), ('b', 's'), (EPS, 'x'), ('c', 'c')]
    dist = edit_distance(a, b)
    assert dist == { 'ins': 1, 'del': 0, 'sub': 1, 'total': 2}

    a = ['a', 'b']
    b = ['b', 'c']
    ali = align(a, b, EPS)
    assert ali == [('a', EPS), ('b', 'b'), (EPS, 'c')]
    dist = edit_distance(a, b)
    assert dist == {'ins': 1, 'del': 1, 'sub': 0, 'total': 2}

    a = ['A' ,'B','C']
    b = ['D' ,'C', 'A']
    ali = align(a, b, EPS)
    assert ali == [('A', 'D'), ('B', EPS), ('C', 'C'), (EPS, 'A')]
    dist = edit_distance(a, b)
    assert dist == {'ins': 1, 'del': 1, 'sub': 1, 'total': 3}


    a = ['A', 'B', 'C',  'D']
    b = ['C', 'E', 'D', 'F']
    ali = align(a, b, EPS)
    assert ali == [('A', EPS), ('B', EPS), ('C', 'C'), (EPS, 'E'), ('D', 'D'), (EPS, 'F')]
    dist = edit_distance(a, b)
    assert dist == {'ins': 2, 'del': 2, 'sub': 0, 'total': 4}


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

def test_edit_distance_sclite():
    a = ['a', 'b']
    b = ['b', 'c']
    results = edit_distance(a, b, sclite_mode=True)
    assert results == {
        'ins': 1,
        'del': 1,
        'sub': 0,
        'total': 2
    }


if __name__ == '__main__':
    test_align()
    test_edit_distance()

