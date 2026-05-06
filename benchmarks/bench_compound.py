"""
Benchmark: compound-aware WER (C++ string-based) vs standard WER (C++ int-based).

Generates a synthetic dataset of sentence pairs with random compound merges,
then times both edit_distance paths over all pairs.

Usage:
    python benchmarks/bench_compound.py
"""

import random
import time

from kaldialign import edit_distance

# fmt: off
VOCAB = [
    "the", "a", "an", "is", "was", "are", "were", "has", "have", "had",
    "do", "does", "did", "will", "would", "can", "could", "may", "might",
    "shall", "should", "must", "be", "been", "being", "get", "got",
    "go", "going", "come", "make", "take", "give", "see", "know",
    "think", "say", "tell", "find", "want", "use", "put", "work",
    "call", "try", "ask", "need", "run", "move", "live", "turn",
    "play", "point", "read", "show", "change", "set", "help", "name",
    "line", "end", "hand", "home", "side", "head", "eye", "back",
    "door", "room", "face", "water", "white", "paper", "long", "over",
    "black", "little", "right", "old", "big", "high", "new", "small",
]
# fmt: on


def generate_dataset(n_pairs, min_len, max_len, compound_prob, seed):
    """
    Generate synthetic ref/hyp pairs.

    With probability ``compound_prob``, 2-3 adjacent ref words are fused
    into a single hyp word (or vice versa), exercising compound matching.
    """
    rng = random.Random(seed)
    pairs = []

    for _ in range(n_pairs):
        length = rng.randint(min_len, max_len)
        ref = [rng.choice(VOCAB) for _ in range(length)]
        hyp = list(ref)  # start from a copy

        # Randomly introduce substitutions (10% of words).
        for i in range(len(hyp)):
            if rng.random() < 0.1:
                hyp[i] = rng.choice(VOCAB)

        # Randomly introduce compound merges.
        if rng.random() < compound_prob:
            n_merges = rng.randint(1, max(1, length // 5))
            for _ in range(n_merges):
                if len(hyp) < 3:
                    break
                merge_len = rng.randint(2, min(3, len(hyp)))
                pos = rng.randint(0, len(hyp) - merge_len)
                merged = "".join(hyp[pos : pos + merge_len])
                hyp = hyp[:pos] + [merged] + hyp[pos + merge_len :]

        pairs.append((ref, hyp))

    return pairs


def bench(pairs, label, **kwargs):
    """Time edit_distance over all pairs, print results."""
    # Warmup
    for ref, hyp in pairs[:10]:
        edit_distance(ref, hyp, **kwargs)

    start = time.perf_counter()
    for ref, hyp in pairs:
        edit_distance(ref, hyp, **kwargs)
    elapsed = time.perf_counter() - start

    n = len(pairs)
    print(
        f"  {label:30s}  total={elapsed:.4f}s  "
        f"per_pair={elapsed / n * 1e6:.1f}us  "
        f"({n} pairs)"
    )
    return elapsed


def main():
    for n_pairs in [500, 1000, 2000]:
        print(f"\n--- {n_pairs} pairs (10-30 words each) ---")
        pairs = generate_dataset(
            n_pairs=n_pairs,
            min_len=10,
            max_len=30,
            compound_prob=0.3,
            seed=42,
        )
        t_std = bench(pairs, "C++ standard (int-based)", merge_compounds=False)
        t_cmp = bench(pairs, "C++ compound (string-based)", merge_compounds=True)
        print(f"  {'overhead ratio':30s}  {t_cmp / t_std:.2f}x")


if __name__ == "__main__":
    main()
