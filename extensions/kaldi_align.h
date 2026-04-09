#include <algorithm>
#include <string>
#include <utility>
#include <vector>
#include <cassert>

#define INS_COST 1
#define DEL_COST 1
#define SUB_COST 1

#define INS_COST_SCLITE 3
#define DEL_COST_SCLITE 3
#define SUB_COST_SCLITE 4

/// Reverses the contents of a vector.
template <typename T>
inline void ReverseVector(std::vector<T> *vec) {
  assert(vec != NULL);
  size_t sz = vec->size();
  for (size_t i = 0; i < sz/2; i++)
    std::swap( (*vec)[i], (*vec)[sz-1-i]);
}

struct error_stats {
  int ins_num;
  int del_num;
  int sub_num;
  int total_num; // total number of errors.
  int total_cost;  // minimum total cost to the current alignment.
};
// Note that both hyp and ref should not contain noise word in
// the following implementation.


int LevenshteinEditDistance(const std::vector<int> &ref,
                            const std::vector<int> &hyp,
                            const bool sclite_mode,
                            int *ins, int *del, int *sub);


int LevenshteinAlignment(const std::vector<int> &a,
                         const std::vector<int> &b,
                         int eps_symbol,
                         const bool sclite_mode,
                         std::vector<std::pair<int, int> > *output);


// Compound-aware variants (string-based).
// Adjacent words in either sequence can be concatenated to match a single
// word in the other sequence at zero cost.

int LevenshteinEditDistanceCompound(
    const std::vector<std::string> &ref,
    const std::vector<std::string> &hyp,
    const bool sclite_mode,
    int *ins, int *del, int *sub);

int LevenshteinAlignmentCompound(
    const std::vector<std::string> &a,
    const std::vector<std::string> &b,
    const std::string &eps_symbol,
    const bool sclite_mode,
    std::vector<std::pair<std::string, std::string>> *output);


namespace internal{
    std::vector<std::pair<int, int>> GetEdits(
        const std::vector<std::vector<int>> &refs,
        const std::vector<std::vector<int>> &hyps
    );

    std::vector<std::pair<int, int>> GetEditsCompound(
        const std::vector<std::vector<std::string>> &refs,
        const std::vector<std::vector<std::string>> &hyps
    );

    std::pair<double, double> GetBootstrapWerInterval(
        const std::vector<std::pair<int, int>> &edit_sym_per_hyp,
        const int replications,
        const unsigned int seed
    );

    double GetPImprov(
        const std::vector<std::pair<int, int>> &edit_sym_per_hyp,
        const std::vector<std::pair<int, int>> &edit_sym_per_hyp2,
        const int replications,
        const unsigned int seed
    );
}
