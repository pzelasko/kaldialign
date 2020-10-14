#cython: language_level=3
from cython.operator cimport address, dereference

from libcpp cimport bool
from libcpp.memory cimport shared_ptr
from libcpp.memory cimport unique_ptr
from libcpp.string cimport string
from libcpp.utility cimport pair
from libcpp.vector cimport vector

from extensions.calign cimport LevenshteinAlignment
from extensions.calign cimport LevenshteinEditDistance


cpdef edit_distance(a, b):
    int2sym = dict(enumerate(sorted(set(a) | set(b))))
    sym2int = {v: k for k, v in int2sym.items()}

    cdef vector[int] ai
    cdef vector[int] bi
    for sym in a:
        ai.push_back(sym2int[sym])
    for sym in b:
        bi.push_back(sym2int[sym])

    cdef int ins_ = 0
    cdef int del_ = 0
    cdef int sub_ = 0
    cdef int total = 0
    total = LevenshteinEditDistance(ai, bi, address(ins_), address(del_), address(sub_))

    return {'ins': ins_, 'del': del_, 'sub': sub_, 'total': total}


cpdef align(a, b, eps_symbol):
    int2sym = dict(enumerate(sorted(set(a) | set(b) | {eps_symbol})))
    sym2int = {v: k for k, v in int2sym.items()}

    cdef vector[int] ai
    cdef vector[int] bi
    for sym in a:
        ai.push_back(sym2int[sym])
    for sym in b:
        bi.push_back(sym2int[sym])

    cdef vector[pair[int, int]] alignment
    cdef int eps_int = sym2int[eps_symbol]
    LevenshteinAlignment(ai, bi, eps_int, address(alignment))

    ali = []
    cdef size_t idx = 0
    for idx in range(alignment.size()):
        ali.append((int2sym[alignment[idx].first], int2sym[alignment[idx].second]))
    return ali
