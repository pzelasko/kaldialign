#include "kaldi_align.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
namespace py = pybind11;

static py::dict EditDistance(const std::vector<int> &a,
                             const std::vector<int> &b,
                             const bool sclite_mode) {
  int ins;
  int del;
  int sub;

  int total = LevenshteinEditDistance(a, b, sclite_mode, &ins, &del, &sub);
  py::dict ans;
  ans["ins"] = ins;
  ans["del"] = del;
  ans["sub"] = sub;
  ans["total"] = total;
  return ans;
}

static std::vector<std::pair<int, int>>
Align(const std::vector<int> &a, const std::vector<int> &b, int eps_symbol, const bool sclite_mode) {
  std::vector<std::pair<int, int>> ans;
  LevenshteinAlignment(a, b, eps_symbol, sclite_mode, &ans);
  return ans;
}

static std::vector<std::pair<int, int>> GetEdits(const std::vector<std::vector<int>> &refs, const std::vector<std::vector<int>> &hyps) {
    return internal::GetEdits(refs, hyps);
}

static py::tuple GetBootstrapWerInterval(const std::vector<std::pair<int, int>> &edit_sym_per_hyp, const int replications, const unsigned int seed) {
    const auto ans = internal::GetBootstrapWerInterval(edit_sym_per_hyp, replications, seed);
    return py::make_tuple(ans.first, ans.second);
}

static double GetPImprov(const std::vector<std::pair<int, int>> &edit_sym_per_hyp, const std::vector<std::pair<int, int>> &edit_sym_per_hyp2, const int replications, const unsigned int seed) {
    return internal::GetPImprov(edit_sym_per_hyp, edit_sym_per_hyp2, replications, seed);
}

PYBIND11_MODULE(_kaldialign, m) {
  m.doc() = "Python wrapper for kaldialign";
  m.def("edit_distance", &EditDistance, py::arg("a"), py::arg("b"), py::arg("sclite_mode") = false);
  m.def("align", &Align, py::arg("a"), py::arg("b"), py::arg("eps_symbol"), py::arg("sclite_mode") = false);
  m.def("_get_edits", &GetEdits, py::arg("refs"), py::arg("hyps"));
  m.def("_get_boostrap_wer_interval", &GetBootstrapWerInterval, py::arg("edit_sym_per_hyp"), py::arg("replications") = 10000, py::arg("seed") = 0);
  m.def("_get_p_improv", &GetPImprov, py::arg("edit_sym_per_hyp"), py::arg("edit_sym_per_hyp2"), py::arg("replications") = 10000, py::arg("seed") = 0);
}
