from kaldialign import align, edit_distance, bootstrap_wer_ci

EPS = "*"


def test_align():
    a = ["a", "b", "c"]
    b = ["a", "s", "x", "c"]
    ali = align(a, b, EPS)
    assert ali == [("a", "a"), ("b", "s"), (EPS, "x"), ("c", "c")]
    dist = edit_distance(a, b)
    assert dist == {"ins": 1, "del": 0, "sub": 1, "total": 2}

    a = ["a", "b"]
    b = ["b", "c"]
    ali = align(a, b, EPS)
    assert ali == [("a", EPS), ("b", "b"), (EPS, "c")]
    dist = edit_distance(a, b)
    assert dist == {"ins": 1, "del": 1, "sub": 0, "total": 2}

    a = ["A", "B", "C"]
    b = ["D", "C", "A"]
    ali = align(a, b, EPS)
    assert ali == [("A", "D"), ("B", EPS), ("C", "C"), (EPS, "A")]
    dist = edit_distance(a, b)
    assert dist == {"ins": 1, "del": 1, "sub": 1, "total": 3}

    a = ["A", "B", "C", "D"]
    b = ["C", "E", "D", "F"]
    ali = align(a, b, EPS)
    assert ali == [
        ("A", EPS),
        ("B", EPS),
        ("C", "C"),
        (EPS, "E"),
        ("D", "D"),
        (EPS, "F"),
    ]
    dist = edit_distance(a, b)
    assert dist == {"ins": 2, "del": 2, "sub": 0, "total": 4}


def test_edit_distance():
    a = ["a", "b", "c"]
    b = ["a", "s", "x", "c"]
    results = edit_distance(a, b)
    assert results == {"ins": 1, "del": 0, "sub": 1, "total": 2}


def test_edit_distance_sclite():
    a = ["a", "b"]
    b = ["b", "c"]
    results = edit_distance(a, b, sclite_mode=True)
    assert results == {"ins": 1, "del": 1, "sub": 0, "total": 2}


def test_bootstrap_wer_ci_1system():
    ref = [
        ("a", "b", "c"),
        ("d", "e", "f"),
    ]

    hyp = [
        ("a", "b", "d"),
        ("e", "f", "f"),
    ]

    ans = bootstrap_wer_ci(ref, hyp)

    assert ans["wer"] == 0.4989
    assert ans["ci95"] == 0.2312
    assert ans["ci95min"] == 0.2678
    assert ans["ci95max"] == 0.7301


def test_bootstrap_wer_ci_2system():
    ref = [
        ("a", "b", "c"),
        ("d", "e", "f"),
    ]

    hyp = [
        ("a", "b", "d"),
        ("e", "f", "f"),
    ]

    hyp2 = [
        ("a", "b", "c"),
        ("e", "e", "f"),
    ]

    ans = bootstrap_wer_ci(ref, hyp, hyp2)

    s = ans["system1"]
    assert s["wer"] == 0.4989
    assert s["ci95"] == 0.2312
    assert s["ci95min"] == 0.2678
    assert s["ci95max"] == 0.7301

    s = ans["system2"]
    assert s["wer"] == 0.1656
    assert s["ci95"] == 0.2312
    assert s["ci95min"] == -0.0656
    assert s["ci95max"] == 0.3968

    assert ans["p_s2_improv_over_s1"] == 1.0


if __name__ == "__main__":
    test_align()
    test_edit_distance()
    test_edit_distance_sclite()
    test_bootstrap_wer_ci_1system()
    test_bootstrap_wer_ci_2system()
