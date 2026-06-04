import math

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


def test_edit_distance_zero_len_ref_zero_err():
    a: list[str] = []
    b: list[str] = []
    results = edit_distance(a, b)
    assert results == {
        "ins": 0,
        "del": 0,
        "sub": 0,
        "total": 0,
        "ref_len": 0,
        "err_rate": 0,
    }


def test_edit_distance_zero_len_ref_with_err():
    a: list[str] = []
    b: list[str] = ["a"]
    results = edit_distance(a, b)
    assert results == {
        "ins": 1,
        "del": 0,
        "sub": 0,
        "total": 1,
        "ref_len": 0,
        "err_rate": float("inf"),
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

def approx(x: float, target: float) -> bool:
    return math.isclose(x, target, abs_tol=3e-3)


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

    assert approx(ans["wer"], 0.50)
    assert approx(ans["ci95"], 0.23)
    assert approx(ans["ci95min"], 0.269)
    assert approx(ans["ci95max"], 0.731)


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
    assert approx(s["wer"], 0.50)
    assert approx(s["ci95"], 0.23)
    assert approx(s["ci95min"], 0.269)
    assert approx(s["ci95max"], 0.731)


    s = ans["system2"]
    assert approx(s["wer"], 0.166)
    assert approx(s["ci95"], 0.231)
    assert approx(s["ci95min"], -0.064)
    assert approx(s["ci95max"], 0.397)

    assert ans["p_s2_improv_over_s1"] == 1.0


# --- Compound word matching tests ---


def test_edit_distance_compound_basic():
    """Two ref words concatenate to match one hyp word."""
    ref = ["white", "paper"]
    hyp = ["whitepaper"]
    dist = edit_distance(ref, hyp, merge_compounds=True)
    assert dist == {
        "ins": 0,
        "del": 0,
        "sub": 0,
        "total": 0,
        "ref_len": 2,
        "err_rate": 0.0,
    }


def test_edit_distance_compound_reverse():
    """One ref word matches two concatenated hyp words."""
    ref = ["whitepaper"]
    hyp = ["white", "paper"]
    dist = edit_distance(ref, hyp, merge_compounds=True)
    assert dist["total"] == 0
    assert dist["ref_len"] == 1
    assert dist["err_rate"] == 0.0


def test_edit_distance_compound_mixed():
    """Mix of compound matches and normal errors."""
    ref = ["the", "white", "paper", "is", "here"]
    hyp = ["the", "whitepaper", "was", "here"]
    dist = edit_distance(ref, hyp, merge_compounds=True)
    assert dist["total"] == 1
    assert dist["sub"] == 1
    assert dist["ins"] == 0
    assert dist["del"] == 0


def test_edit_distance_compound_three_words():
    """Three ref words concatenate to match one hyp word."""
    ref = ["a", "b", "c"]
    hyp = ["abc"]
    dist = edit_distance(ref, hyp, merge_compounds=True)
    assert dist["total"] == 0


def test_edit_distance_compound_no_false_positive():
    """Without merge_compounds, normal edit distance applies."""
    ref = ["white", "paper"]
    hyp = ["whitepaper"]
    dist = edit_distance(ref, hyp, merge_compounds=False)
    assert dist["total"] == 2  # 1 sub + 1 del


def test_edit_distance_compound_sclite():
    """sclite_mode affects path selection but compound match is still 0 cost."""
    ref = ["white", "paper", "is", "here"]
    hyp = ["whitepaper", "was", "here"]
    dist_normal = edit_distance(ref, hyp, merge_compounds=True)
    dist_sclite = edit_distance(ref, hyp, sclite_mode=True, merge_compounds=True)
    assert dist_normal["total"] == 1
    assert dist_sclite["total"] == 1


def test_align_compound():
    ref = ["white", "paper"]
    hyp = ["whitepaper"]
    ali = align(ref, hyp, EPS, merge_compounds=True)
    assert ali == [("white paper", "whitepaper")]


def test_align_compound_reverse():
    ref = ["whitepaper"]
    hyp = ["white", "paper"]
    ali = align(ref, hyp, EPS, merge_compounds=True)
    assert ali == [("whitepaper", "white paper")]


def test_align_compound_mixed():
    ref = ["the", "white", "paper", "is", "here"]
    hyp = ["the", "whitepaper", "was", "here"]
    ali = align(ref, hyp, EPS, merge_compounds=True)
    assert ali == [
        ("the", "the"),
        ("white paper", "whitepaper"),
        ("is", "was"),
        ("here", "here"),
    ]


def test_bootstrap_wer_ci_compound():
    ref = [
        ("white", "paper"),
        ("hello", "world"),
    ]
    hyp = [
        ("whitepaper",),
        ("helloworld",),
    ]
    ans = bootstrap_wer_ci(ref, hyp, merge_compounds=True)
    assert approx(ans["wer"], 0.0)
