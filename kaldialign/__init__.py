import math
import random
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, TypeVar, Union

import _kaldialign

Symbol = TypeVar("Symbol")


def edit_distance(
    ref: Iterable[Symbol], hyp: Iterable[Symbol], sclite_mode: bool = False
) -> Dict[str, Union[int, float]]:
    """
    Compute the edit distance between sequences ``ref`` and ``hyp``.
    Both sequences can be strings or lists of strings or ints.

    Optional ``sclite_mode`` sets INS/DEL/SUB costs to 3/3/4 for
    compatibility with sclite tool.

    Returns a dict with keys:
    * ``ins`` -- the number of insertions (in ``hyp`` vs ``ref``)
    * ``del`` -- the number of deletions (in ``hyp`` vs ``ref``)
    * ``sub`` -- the number of substitutions
    * ``total`` -- total number of errors
    * ``ref_len`` -- the number of symbols in ``ref``
    * ``err_rate`` -- the error rate  (total number of errors divided by ``ref_len``)
    """
    int2sym = dict(enumerate(sorted(set(ref) | set(hyp))))
    sym2int = {v: k for k, v in int2sym.items()}

    refi: List[int] = []
    hypi: List[int] = []
    for sym in ref:
        refi.append(sym2int[sym])

    for sym in hyp:
        hypi.append(sym2int[sym])

    ans = _kaldialign.edit_distance(refi, hypi, sclite_mode)
    ans["ref_len"] = len(refi)
    ans["err_rate"] = ans["total"] / len(refi)
    return ans


def align(
    ref: Iterable[Symbol],
    hyp: Iterable[Symbol],
    eps_symbol: Symbol,
    sclite_mode: bool = False,
) -> List[Tuple[Symbol, Symbol]]:
    """
    Compute the alignment between sequences ``ref`` and ``hyp``.
    Both sequences can be strings or lists of strings or ints.

    ``eps_symbol`` is used as a blank symbol to indicate insertion or deletion.

    Optional ``sclite_mode`` sets INS/DEL/SUB costs to 3/3/4 for
    compatibility with sclite tool.

    Returns a list of pairs of alignment symbols. The presence of ``eps_symbol``
    in the first pair index indicates insertion, and in the second pair index, deletion.
    Mismatched symbols indicate substitution.
    """
    int2sym = dict(enumerate(sorted(set(ref) | set(hyp) | {eps_symbol})))
    sym2int = {v: k for k, v in int2sym.items()}

    ai: List[int] = []
    bi: List[int] = []

    for sym in ref:
        ai.append(sym2int[sym])

    for sym in hyp:
        bi.append(sym2int[sym])

    eps_int = sym2int[eps_symbol]
    alignment: List[Tuple[int, int]] = _kaldialign.align(ai, bi, eps_int, sclite_mode)

    ali = []
    for idx in range(len(alignment)):
        ali.append((int2sym[alignment[idx][0]], int2sym[alignment[idx][1]]))

    return ali


def bootstrap_wer_ci(
    refs: Sequence[Sequence[Symbol]],
    hyps: Sequence[Sequence[Symbol]],
    hyps2: Optional[Sequence[Sequence[Symbol]]] = None,
    replications: int = 10000,
    seed: int = 0,
) -> Dict:
    """
    Compute a boostrapping of WER to extract the 95% confidence interval (CI)
    using the bootstrap method of Bisani and Ney [1].
    The implementation is based on Kaldi's ``compute-wer-bootci`` script [2].

    Args:
        refs: A list of reference sequences (str, list[str], list[list[[int]])
        hyps: A list of hypothesis sequences from system1 (str, list[str], list[list[int]])
        hyps2: A list of hypothesis sequences from system2 (str, list[str], list[list[int]]).
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
    from _kaldialign import _get_boostrap_wer_interval, _get_edits, _get_p_improv

    assert len(hyps) == len(
        refs
    ), f"Inconsistent number of reference ({len(refs)}) and hypothesis ({len(hyps)}) sequences."
    assert replications > 0, "The number of replications must be greater than 0."
    assert seed >= 0, "The seed must be 0 or greater."
    assert not isinstance(refs, str) and not isinstance(
        hyps, str
    ), "The input must be a list of strings or list of lists of ints."

    refs, hyps, hyps2 = _convert_to_int(refs, hyps, hyps2)

    edit_sym_per_hyp = _get_edits(refs, hyps)
    mean, interval = _get_boostrap_wer_interval(
        edit_sym_per_hyp, replications=replications, seed=seed
    )
    ans1 = _build_results(mean, interval)
    if hyps2 is None:
        return ans1

    assert len(hyps2) == len(
        refs
    ), f"Inconsistent number of reference ({len(refs)}) and hypothesis ({len(hyps2)}) sequences for the second system (hyp2_seqs)."
    edit_sym_per_hyp2 = _get_edits(refs, hyps2)
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


def _build_results(mean: float, interval: float) -> Dict[str, float]:
    return {
        "wer": mean,
        "ci95": interval,
        "ci95min": mean - interval,
        "ci95max": mean + interval,
    }


def _convert_to_int(
    ref: Sequence[Sequence[Symbol]],
    hyp: Sequence[Sequence[Symbol]],
    hyp2: Sequence[Sequence[Symbol]] = None,
) -> Tuple[List[List[Symbol]], ...]:
    sources = [ref, hyp]
    if hyp2 is not None:
        sources.append(hyp2)

    symbols = sorted(
        set(symbol for source in sources for seq in source for symbol in seq)
    )
    int2sym = dict(enumerate(symbols))
    sym2int = {v: k for k, v in int2sym.items()}

    ints = [[[sym2int[item] for item in seq] for seq in source] for source in sources]
    if hyp2 is None:
        ints.append(None)
    return tuple(ints)
