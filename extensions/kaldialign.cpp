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

PYBIND11_MODULE(_kaldialign, m) {
  m.doc() = "Python wrapper for kaldialign";
  m.def("edit_distance", &EditDistance, py::arg("a"), py::arg("b"), py::arg("sclite_mode") = false);
  m.def("align", &Align, py::arg("a"), py::arg("b"), py::arg("eps_symbol"), py::arg("sclite_mode") = false);
}
