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

- `align(seq1, seq2, epsilon)` - used to obtain the alignment between two string sequences. `epsilon` should be a null symbol (indicating deletion/insertion) that doesn't exist in either sequence.

```python
from kaldialign import align

EPS = '*'
a = ['a', 'b', 'c']
b = ['a', 's', 'x', 'c']
ali = align(a, b, EPS)
assert ali == [('a', 'a'), ('b', 's'), (EPS, 'x'), ('c', 'c')]
```

- `edit_distance(seq1, seq2)` - used to obtain the total edit distance, as well as the number of insertions, deletions and substitutions.

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

- For both of the above examples, you can pass `sclite_mode=True` to compute WER or alignments
based on SCLITE style weights, i.e., insertion/deletion cost 3 and substitution cost 4.

## Motivation

The need for this arised from the fact that practically all implementations of the Levenshtein distance have slight differences, making it impossible to use a different scoring tool than Kaldi and get the same error rate results. This package copies code from Kaldi directly and wraps it using Cython, avoiding the issue altogether.
