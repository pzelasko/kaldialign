#cython: language_level=3
from libcpp.utility cimport pair
from libcpp.vector cimport vector

cdef extern from "kaldi_align.h" nogil:

    int LevenshteinEditDistance(
            const vector[int] &a,
            const vector[int] &b,
            int *ins_,
            int *del_,
            int *sub_,
    )

    int LevenshteinAlignment(
            const vector[int] &a,
            const vector[int] &b,
            int eps_symbol,
            vector[pair[int, int]] *output
    )
