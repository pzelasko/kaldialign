#include "kaldi_align.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
namespace py = pybind11;

static py::dict EditDistance(const std::vector<int> &a,
                             const std::vector<int> &b) {
  int ins;
  int del;
  int sub;

  int total = LevenshteinEditDistance(a, b, &ins, &del, &sub);
  py::dict ans;
  ans["ins"] = ins;
  ans["del"] = del;
  ans["sub"] = sub;
  ans["total"] = total;
  return ans;
}

static std::vector<std::pair<int, int>>
Align(const std::vector<int> &a, const std::vector<int> &b, int eps_symbol) {
  std::vector<std::pair<int, int>> ans;
  LevenshteinAlignment(a, b, eps_symbol, &ans);
  return ans;
}

PYBIND11_MODULE(_kaldialign, m) {
  m.doc() = "Python wrapper for kaldialign";
  m.def("edit_distance", &EditDistance, py::arg("a"), py::arg("b"));
  m.def("align", &Align, py::arg("a"), py::arg("b"), py::arg("eps_symbol"));
}
