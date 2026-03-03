from collections.abc import Sequence

def edit_distance(
    a: Sequence[int],
    b: Sequence[int],
    sclite_mode: bool = False
) -> dict[str, int]: ...

def align(
    a: Sequence[int],
    b: Sequence[int],
    eps_symbol: int,
    sclite_mode: bool = False
) -> list[tuple[int, int]]: ...

def _get_edits(
    refs: Sequence[Sequence[int]],
    hyps: Sequence[Sequence[int]]
) -> list[tuple[int, int]]: ...

def _get_boostrap_wer_interval(
    edit_sym_per_hyp: Sequence[tuple[int, int]],
    replications: int = 10000,
    seed: int = 0
) -> tuple[float, float]: ...

def _get_p_improv(
    edit_sym_per_hyp: Sequence[tuple[int, int]],
    edit_sym_per_hyp2: Sequence[tuple[int, int]],
    replications: int = 10000,
    seed: int = 0
) -> float: ...
