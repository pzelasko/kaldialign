from typing import List
import _kaldialign


def edit_distance(a, b):
    int2sym = dict(enumerate(sorted(set(a) | set(b))))
    sym2int = {v: k for k, v in int2sym.items()}

    ai: List[int] = []
    bi: List[int] = []
    for sym in a:
        ai.append(sym2int[sym])

    for sym in b:
        bi.append(sym2int[sym])

    return _kaldialign.edit_distance(ai, bi)


def align(a, b, eps_symbol):
    int2sym = dict(enumerate(sorted(set(a) | set(b) | {eps_symbol})))
    sym2int = {v: k for k, v in int2sym.items()}

    ai: List[int] = []
    bi: List[int] = []

    for sym in a:
        ai.append(sym2int[sym])

    for sym in b:
        bi.append(sym2int[sym])

    eps_int = sym2int[eps_symbol]
    alignment: List[Tuple[int, int]] = _kaldialign.align(ai, bi, eps_int)

    ali = []
    idx = 0
    for idx in range(len(alignment)):
        ali.append((int2sym[alignment[idx][0]], int2sym[alignment[idx][1]]))

    return ali
