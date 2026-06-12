# kaldialign

A small package that exposes edit distance computation functions from [Kaldi](https://github.com/kaldi-asr/kaldi). It uses the original Kaldi code and wraps it using pybind11.

## Installation

```bash
conda install -c kaldialign kaldialign
```

or

```bash
pip install --verbose kaldialign
```

or

```bash
pip install --verbose -U git+https://github.com/pzelasko/kaldialign.git
```

or

```bash
git clone https://github.com/pzelasko/kaldialign.git
cd kaldialign
python3 -m pip install --verbose .
```

## Examples

### Alignment

`align(ref, hyp, epsilon)` - used to obtain the alignment between two string sequences. `epsilon` should be a null symbol (indicating deletion/insertion) that doesn't exist in either sequence.

```python
from kaldialign import align

EPS = '*'
a = ['a', 'b', 'c']
b = ['a', 's', 'x', 'c']
ali = align(a, b, EPS)
assert ali == [('a', 'a'), ('b', 's'), (EPS, 'x'), ('c', 'c')]
```

### Edit distance

`edit_distance(ref, hyp)` - used to obtain the total edit distance, as well as the number of insertions, deletions and substitutions.

```python
from kaldialign import edit_distance

a = ['a', 'b', 'c']
b = ['a', 's', 'x', 'c']
results = edit_distance(a, b)
assert results == {
    'ins': 1,
    'del': 0,
    'sub': 1,
    'total': 2
}
```

### Batch error rate

`batch_error_rate(refs, hyps)` - used to obtain corpus-level error counts and error rate for a batch of reference/hypothesis sequence pairs. It computes error rate as the sum of all insertions, deletions, and substitutions divided by the total number of reference symbols.

```python
from kaldialign import batch_error_rate

refs = [
    ("a", "b", "c"),
    ("d", "e"),
]
hyps = [
    ("a", "x", "c", "y"),
    ("d",),
]
results = batch_error_rate(refs, hyps)
assert results == {
    "ins": 1,
    "del": 1,
    "sub": 1,
    "total": 3,
    "ref_len": 5,
    "err_rate": 0.6,
}
```

For alignment, edit distance, and batch error rate, you can pass `sclite_mode=True` to compute
WER or alignments based on SCLITE style weights, i.e., insertion/deletion cost 3 and substitution cost 4.

### Compound word matching

All functions accept `merge_compounds=True` to allow adjacent words in either sequence to be
concatenated (without separator) to match a single word in the other sequence at zero cost.
This is useful whenever there are inconsistencies within transcriptions,
or between training and testing conditions of a model evaluated with WER.

```python
from kaldialign import edit_distance, align

# "white paper" (2 words) matches "whitepaper" (1 word) with 0 errors
ref = ["the", "white", "paper", "is", "good"]
hyp = ["the", "whitepaper", "is", "good"]

results = edit_distance(ref, hyp, merge_compounds=True)
assert results["total"] == 0

# Works in both directions
results = edit_distance(hyp, ref, merge_compounds=True)
assert results["total"] == 0

# Alignment shows compound matches as space-joined strings
ali = align(ref, hyp, "*", merge_compounds=True)
assert ali == [
    ("the", "the"),
    ("white paper", "whitepaper"),
    ("is", "is"),
    ("good", "good"),
]
```

### Bootstrapping method to extract WER 95% confidence intervals

`boostrap_wer_ci(ref, hyp, hyp2=None)` - obtain the 95% confidence intervals for WER using Bisani and Ney boostrapping method.

```python
from kaldialign import bootstrap_wer_ci

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
```

All bootstrap functions also accept `merge_compounds=True`.

It also supports providing hypotheses from system 1 and system 2 to compute the probability of S2 improving over S1:

```python
from kaldialign import bootstrap_wer_ci

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
```

## Motivation

The need for this arised from the fact that practically all implementations of the Levenshtein distance have slight differences, making it impossible to use a different scoring tool than Kaldi and get the same error rate results. This package copies code from Kaldi directly and wraps it using pybind11, avoiding the issue altogether.
