from typing import List, Tuple
import _kaldialign


def edit_distance(a, b, sclite_mode=False):
    int2sym = dict(enumerate(sorted(set(a) | set(b))))
    sym2int = {v: k for k, v in int2sym.items()}

    ai: List[int] = []
    bi: List[int] = []
    for sym in a:
        ai.append(sym2int[sym])

    for sym in b:
        bi.append(sym2int[sym])

    return _kaldialign.edit_distance(ai, bi, sclite_mode)


def align(a, b, eps_symbol, sclite_mode=False):
    int2sym = dict(enumerate(sorted(set(a) | set(b) | {eps_symbol})))
    sym2int = {v: k for k, v in int2sym.items()}

    ai: List[int] = []
    bi: List[int] = []

    for sym in a:
        ai.append(sym2int[sym])

    for sym in b:
        bi.append(sym2int[sym])

    eps_int = sym2int[eps_symbol]
    alignment: List[Tuple[int, int]] = _kaldialign.align(ai, bi, eps_int, sclite_mode)

    ali = []
    idx = 0
    for idx in range(len(alignment)):
        ali.append((int2sym[alignment[idx][0]], int2sym[alignment[idx][1]]))

    return ali
