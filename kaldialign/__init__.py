import math
from typing import List, Tuple
import random
import _kaldialign


def edit_distance(a, b, sclite_mode=False):
    """
    Compute the edit distance between sequences ``a`` and ``b``.
    Both sequences can be strings or lists of strings or ints.

    Optional ``sclite_mode`` sets INS/DEL/SUB costs to 3/3/4 for
    compatibility with sclite tool.

    Returns a dict with keys ``ins``, ``del``, ``sub``, ``total``,
    which stand for the count of insertions, deletions, substitutions,
    and the total number of errors.
    """
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
    """
    Compute the alignment between sequences ``a`` and ``b``.
    Both sequences can be strings or lists of strings or ints.

    ``eps_symbol`` is used as a blank symbol to indicate insertion or deletion.

    Optional ``sclite_mode`` sets INS/DEL/SUB costs to 3/3/4 for
    compatibility with sclite tool.

    Returns a list of pairs of alignment symbols. The presence of ``eps_symbol``
    in the first pair index indicates insertion, and in the second pair index, deletion.
    Mismatched symbols indicate substitution.
    """
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
    for idx in range(len(alignment)):
        ali.append((int2sym[alignment[idx][0]], int2sym[alignment[idx][1]]))

    return ali


def bootstrap_wer_ci(
    ref_seqs, hyp_seqs, hyp2_seqs=None, replications: int = 10000, seed: int = 0
):
    """
    Compute a boostrapping of WER to extract the 95% confidence interval (CI)
    using the bootstrap method of Bisani and Ney [1].
    The implementation is based on Kaldi's ``compute-wer-bootci`` script [2].

    Args:
        ref_seqs: A list of reference sequences (str, list[str], list[int])
        hyp_seqs: A list of hypothesis sequences from system1 (str, list[str], list[int])
        hyp2_seqs: A list of hypothesis sequences from system2 (str, list[str], list[int]).
            When provided, we'll compute CI for both systems as well as the probability
            of system2 improving over system1.
        replications: The number of replications to use for bootstrapping.
        seed: The random seed to reproduce the results.

    Returns:
        A dict with results. When scoring a single system (``hyp2_seqs=None``), the keys are:
            - "wer" (mean WER estimate),
            - "ci95" (95% confidence interval size),
            - "ci95min" (95% confidence interval lower bound)
            - "ci95max" (95% confidence interval upper bound)
        When scoring two systems, the keys are "system1", "system2", and "p_s2_improv_over_s1".
        The first two keys contain dicts as described for the single-system case, and the last key's
        value is a float in the range [0, 1].

    [1] Bisani, M., & Ney, H. (2004, May). Bootstrap estimates for confidence intervals in ASR performance evaluation.
        In 2004 IEEE International Conference on Acoustics, Speech, and Signal Processing (Vol. 1, pp. I-409). IEEE.

    [2] https://github.com/kaldi-asr/kaldi/blob/master/src/bin/compute-wer-bootci.cc
    """
    assert len(hyp_seqs) == len(
        ref_seqs
    ), f"Inconsistent number of reference ({len(ref_seqs)}) and hypothesis ({len(hyp_seqs)}) sequences."
    edit_sym_per_hyp = _get_edits(ref_seqs, hyp_seqs)
    mean, interval = _get_boostrap_wer_interval(
        edit_sym_per_hyp, replications=replications, seed=seed
    )
    ans1 = _build_results(mean, interval)
    if hyp2_seqs is None:
        return ans1

    assert len(hyp2_seqs) == len(
        ref_seqs
    ), f"Inconsistent number of reference ({len(ref_seqs)}) and hypothesis ({len(hyp2_seqs)}) sequences for the second system (hyp2_seqs)."
    edit_sym_per_hyp2 = _get_edits(ref_seqs, hyp2_seqs)
    mean2, interval2 = _get_boostrap_wer_interval(
        edit_sym_per_hyp2, replications=replications, seed=seed
    )
    p_improv = _get_p_improv(
        edit_sym_per_hyp, edit_sym_per_hyp2, replications=replications, seed=seed
    )
    return {
        "system1": ans1,
        "system2": _build_results(mean2, interval2),
        "p_s2_improv_over_s1": p_improv,
    }


def _build_results(mean, interval):
    return {
        "wer": round(mean, ndigits=4),
        "ci95": round(interval, ndigits=4),
        "ci95min": round(mean - interval, ndigits=4),
        "ci95max": round(mean + interval, ndigits=4),
    }


def _get_edits(ref_seqs, hyp_seqs):
    edit_sym_per_hyp = []
    for ref, hyp in zip(ref_seqs, hyp_seqs):
        dist = edit_distance(ref, hyp)
        edit_sym_per_hyp.append((dist["total"], len(ref)))
    return edit_sym_per_hyp


def _get_boostrap_wer_interval(edit_sym_per_hyp, replications, seed):
    rng = random.Random(seed)

    wer_accum, wer_mult_accum = 0.0, 0.0
    for i in range(replications):
        num_sym, num_errs = 0, 0
        for j in range(len(edit_sym_per_hyp)):
            nerr, nsym = rng.choice(edit_sym_per_hyp)
            num_sym += nsym
            num_errs += nerr
        wer_rep = num_errs / num_sym
        wer_accum += wer_rep
        wer_mult_accum += wer_rep**2

    mean = wer_accum / replications
    _tmp = wer_mult_accum / replications - mean**2
    if _tmp < 0:
        interval = 0
    else:
        interval = 1.96 * math.sqrt(_tmp)

    return mean, interval


def _get_p_improv(edit_sym_per_hyp, edit_sym_per_hyp2, replications, seed):
    rng = random.Random(seed)

    improv_accum = 0
    for i in range(replications):
        num_errs = 0
        for j in range(len(edit_sym_per_hyp)):
            pos = rng.randint(0, len(edit_sym_per_hyp) - 1)
            num_errs += edit_sym_per_hyp[pos][0] - edit_sym_per_hyp2[pos][0]
        if num_errs > 0:
            improv_accum += 1

    return improv_accum / replications
