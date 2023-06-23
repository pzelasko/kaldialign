#include "kaldi_align.h"

int LevenshteinEditDistance(const std::vector<int> &ref,
                              const std::vector<int> &hyp,
                              const bool sclite_mode,
                              int *ins, int *del, int *sub) {
  int ins_cost, del_cost, sub_cost;
  if (sclite_mode) {
    ins_cost = INS_COST_SCLITE;
    del_cost = DEL_COST_SCLITE;
    sub_cost = SUB_COST_SCLITE;
  } else {
    ins_cost = INS_COST;
    del_cost = DEL_COST;
    sub_cost = SUB_COST;
  }
  
  // temp sequence to remember error type and stats.
  std::vector<error_stats> e(ref.size()+1);
  std::vector<error_stats> cur_e(ref.size()+1);
  // initialize the first hypothesis aligned to the reference at each
  // position:[hyp_index =0][ref_index]
  for (size_t i =0; i < e.size(); i ++) {
    e[i].ins_num = 0;
    e[i].sub_num = 0;
    e[i].del_num = i;
    e[i].total_num = i;
    e[i].total_cost = i*del_cost;
  }

  // for other alignments
  for (size_t hyp_index = 1; hyp_index <= hyp.size(); hyp_index ++) {
    cur_e[0] = e[0];
    cur_e[0].ins_num++;
    cur_e[0].total_num++;
    cur_e[0].total_cost += ins_cost;
    for (size_t ref_index = 1; ref_index <= ref.size(); ref_index ++) {
      int ins_err = e[ref_index].total_cost + ins_cost;
      int del_err = cur_e[ref_index-1].total_cost + del_cost;
      int sub_err = e[ref_index-1].total_cost;
      if (hyp[hyp_index-1] != ref[ref_index-1])
        sub_err += sub_cost;

      if (sub_err < ins_err && sub_err < del_err) {
        cur_e[ref_index] = e[ref_index-1];
        if (hyp[hyp_index-1] != ref[ref_index-1]) {
          cur_e[ref_index].sub_num++;  // substitution error should be increased
          cur_e[ref_index].total_num++;
        }
        cur_e[ref_index].total_cost = sub_err;
     } else if (del_err < ins_err) {
        cur_e[ref_index] = cur_e[ref_index-1];
        cur_e[ref_index].total_cost = del_err;
        cur_e[ref_index].del_num++;    // deletion number is increased.
        cur_e[ref_index].total_num++;
     } else {
        cur_e[ref_index] = e[ref_index];
        cur_e[ref_index].total_cost = ins_err;
        cur_e[ref_index].ins_num++;    // insertion number is increased.
        cur_e[ref_index].total_num++;
     }
  }
  e = cur_e;  // alternate for the next recursion.
  }
  size_t ref_index = e.size()-1;
  *ins = e[ref_index].ins_num, *del =
    e[ref_index].del_num, *sub = e[ref_index].sub_num;
  return e[ref_index].total_num;
}


int LevenshteinAlignment(const std::vector<int> &a,
                          const std::vector<int> &b,
                          int eps_symbol,
                          const bool sclite_mode,
                          std::vector<std::pair<int, int> > *output) {
  // Check inputs:
  {
    assert(output != NULL);
    for (size_t i = 0; i < a.size(); i++) assert(a[i] != eps_symbol);
    for (size_t i = 0; i < b.size(); i++) assert(b[i] != eps_symbol);
  }
  output->clear();

  int ins_cost, del_cost, sub_cost;
  if (sclite_mode) {
    ins_cost = INS_COST_SCLITE;
    del_cost = DEL_COST_SCLITE;
    sub_cost = SUB_COST_SCLITE;
  } else {
    ins_cost = INS_COST;
    del_cost = DEL_COST;
    sub_cost = SUB_COST;
  }

  // inthis is very memory-inefficiently implemented using a vector of vectors.
  size_t M = a.size(), N = b.size();
  size_t m, n;
  std::vector<std::vector<int> > e(M+1);
  for (m = 0; m <=M; m++) e[m].resize(N+1);
  for (n = 0; n <= N; n++)
    e[0][n]  = n*ins_cost;
  for (m = 1; m <= M; m++) {
    e[m][0] = e[m-1][0] + del_cost;
    for (n = 1; n <= N; n++) {
      int sub_or_ok = e[m-1][n-1] + (a[m-1] == b[n-1] ? 0 : sub_cost);
      int del = e[m-1][n] + del_cost;  // assumes a == ref, b == hyp.
      int ins = e[m][n-1] + ins_cost;
      e[m][n] = std::min(sub_or_ok, std::min(del, ins));
    }
  }
  // get time-reversed output first: trace back.
  m = M;
  n = N;
  while (m != 0 || n != 0) {
    size_t last_m, last_n;
    if (m == 0) {
      last_m = m;
      last_n = n-1;
    } else if (n == 0) {
      last_m = m-1;
      last_n = n;
    } else {
      int sub_or_ok = e[m-1][n-1] + (a[m-1] == b[n-1] ? 0 : sub_cost);
      int del = e[m-1][n] + del_cost;  // assumes a == ref, b == hyp.
      int ins = e[m][n-1] + ins_cost;
      // choose sub_or_ok if all else equal.
      if (sub_or_ok < std::min(del, ins)) {
        last_m = m-1;
        last_n = n-1;
      } else {
        if (del < ins) {  // choose del over ins if equal.
          last_m = m-1;
          last_n = n;
        } else {
          last_m = m;
          last_n = n-1;
        }
      }
    }
    int a_sym, b_sym;
    a_sym = (last_m == m ? eps_symbol : a[last_m]);
    b_sym = (last_n == n ? eps_symbol : b[last_n]);
    output->push_back(std::make_pair(a_sym, b_sym));
    m = last_m;
    n = last_n;
  }
  ReverseVector(output);
  return e[M][N];
}
