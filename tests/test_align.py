from functools import partial

import pytest

from kaldialign import align, bootstrap_wer_ci, edit_distance

EPS = "*"


def test_align():
    a = ["a", "b", "c"]
    b = ["a", "s", "x", "c"]
    ali = align(a, b, EPS)
    assert ali == [("a", "a"), ("b", "s"), (EPS, "x"), ("c", "c")]
    dist = edit_distance(a, b)
    assert dist == {
        "ins": 1,
        "del": 0,
        "sub": 1,
        "total": 2,
        "ref_len": 3,
        "err_rate": 2 / 3,
    }

    a = ["a", "b"]
    b = ["b", "c"]
    ali = align(a, b, EPS)
    assert ali == [("a", EPS), ("b", "b"), (EPS, "c")]
    dist = edit_distance(a, b)
    assert dist == {
        "ins": 1,
        "del": 1,
        "sub": 0,
        "total": 2,
        "ref_len": 2,
        "err_rate": 1.0,
    }

    a = ["A", "B", "C"]
    b = ["D", "C", "A"]
    ali = align(a, b, EPS)
    assert ali == [("A", "D"), ("B", EPS), ("C", "C"), (EPS, "A")]
    dist = edit_distance(a, b)
    assert dist == {
        "ins": 1,
        "del": 1,
        "sub": 1,
        "total": 3,
        "ref_len": 3,
        "err_rate": 1.0,
    }

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
    assert dist == {
        "ins": 2,
        "del": 2,
        "sub": 0,
        "total": 4,
        "ref_len": 4,
        "err_rate": 1.0,
    }


def test_edit_distance():
    a = ["a", "b", "c"]
    b = ["a", "s", "x", "c"]
    results = edit_distance(a, b)
    assert results == {
        "ins": 1,
        "del": 0,
        "sub": 1,
        "total": 2,
        "ref_len": 3,
        "err_rate": 2 / 3,
    }


def test_edit_distance_sclite():
    a = ["a", "b"]
    b = ["b", "c"]
    results = edit_distance(a, b, sclite_mode=True)
    assert results == {
        "ins": 1,
        "del": 1,
        "sub": 0,
        "total": 2,
        "ref_len": 2,
        "err_rate": 1.0,
    }


approx = partial(pytest.approx, abs=1e-3)


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
    print(ans)

    assert ans["wer"] == approx(0.50)
    assert ans["ci95"] == approx(0.23)
    assert ans["ci95min"] == approx(0.269)
    assert ans["ci95max"] == approx(0.731)


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
    print(ans)

    s = ans["system1"]
    assert s["wer"] == approx(0.50)
    assert s["ci95"] == approx(0.23)
    assert s["ci95min"] == approx(0.269)
    assert s["ci95max"] == approx(0.731)

    s = ans["system2"]
    assert s["wer"] == approx(0.166)
    assert s["ci95"] == approx(0.231)
    assert s["ci95min"] == approx(-0.064)
    assert s["ci95max"] == approx(0.397)

    assert ans["p_s2_improv_over_s1"] == 1.0


if __name__ == "__main__":
    test_align()
    test_edit_distance()
    test_edit_distance_sclite()
    test_bootstrap_wer_ci_1system()
    test_bootstrap_wer_ci_2system()
