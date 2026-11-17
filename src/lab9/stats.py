"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.stats import bootstrap

POS = "FAIL"  # FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """Return tp/fp/fn/tn with FAIL as the positive class."""

    if len(human) != len(judge):
        raise ValueError("human and judge must have the same length")

    tp = fp = fn = tn = 0

    for actual, predicted in zip(human, judge):
        if actual == POS and predicted == POS:
            tp += 1
        elif actual != POS and predicted == POS:
            fp += 1
        elif actual == POS and predicted != POS:
            fn += 1
        else:
            tn += 1

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }


def precision_recall(
    human: Sequence[str],
    judge: Sequence[str]
) -> tuple[float, float]:
    """
    Calculate precision and recall.

    Precision = TP / (TP + FP)
    Recall    = TP / (TP + FN)

    Return 0.0 if the denominator is zero.
    """

    counts = confusion(human, judge)

    tp = counts["tp"]
    fp = counts["fp"]
    fn = counts["fn"]

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """
    Calculate Cohen's Kappa.

    Kappa = (p_o - p_e) / (1 - p_e)

    Raise ValueError when kappa is undefined.
    A constant judge must not pass calibration.
    """

    if len(human) != len(judge):
        raise ValueError("human and judge must have the same length")

    if len(human) == 0:
        raise ValueError("Cannot calculate kappa for empty sequences")

    counts = confusion(human, judge)
    n = len(human)

    # Observed agreement
    po = (counts["tp"] + counts["tn"]) / n

    # Actual class proportions
    human_fail = (counts["tp"] + counts["fn"]) / n
    human_pass = (counts["fp"] + counts["tn"]) / n

    # Predicted class proportions
    judge_fail = (counts["tp"] + counts["fp"]) / n
    judge_pass = (counts["fn"] + counts["tn"]) / n

    # Expected agreement by chance
    pe = (
        human_fail * judge_fail
        + human_pass * judge_pass
    )

    if pe == 1.0:
        raise ValueError(
            "Cohen's Kappa is undefined because expected agreement is 1"
        )

    return (po - pe) / (1.0 - pe)


def rogan_gladen(
    observed_rate: float,
    sensitivity: float,
    specificity: float
) -> float:
    """
    Correct an observed failure rate for judge error.

    Rogan-Gladen estimator:
        prevalence = (observed_rate + specificity - 1)
                     / (sensitivity + specificity - 1)

    Clip the result to [0, 1].
    """

    for name, value in (
        ("observed_rate", observed_rate),
        ("sensitivity", sensitivity),
        ("specificity", specificity),
    ):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be between 0 and 1")

    denominator = sensitivity + specificity - 1.0

    if denominator == 0.0:
        raise ValueError(
            "Rogan-Gladen is undefined when sensitivity + specificity = 1"
        )

    corrected_rate = (
        observed_rate + specificity - 1.0
    ) / denominator

    return max(0.0, min(1.0, corrected_rate))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    # TODO M4
    # raise NotImplementedError
    if len(a) != len(b):
        raise ValueError("a and b must have the same length")

    if len(a) == 0:
        raise ValueError("a and b must not be empty")

    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")

    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")

    a_array = np.asarray(a, dtype=float)
    b_array = np.asarray(b, dtype=float)

    # Identical arrays have exactly zero difference.
    if np.array_equal(a_array, b_array):
        return 0.0, 0.0, 0.0

    # Statistic: mean difference between paired samples.
    def mean_difference(x, y, axis=-1):
        return np.mean(x - y, axis=axis)

    result = bootstrap(
        data=(a_array, b_array),
        statistic=mean_difference,
        paired=True,
        vectorized=True,
        n_resamples=n_resamples,
        confidence_level=confidence,
        method="percentile",
        rng=np.random.default_rng(rng),
    )

    difference = float(np.mean(a_array) - np.mean(b_array))
    lower = float(result.confidence_interval.low)
    upper = float(result.confidence_interval.high)

    return difference, lower, upper


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    # TODO M6
    # raise NotImplementedError
    import math

    if n <= 0 or c < 0 or c > n or k <= 0 or k > n:
        raise ValueError("Require n > 0, 0 <= c <= n, and 1 <= k <= n")
    if c == 0:
        return 0.0
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    # TODO M6
    # raise NotImplementedError
    import math

    if n <= 0 or c < 0 or c > n or k <= 0 or k > n:
        raise ValueError("Require n > 0, 0 <= c <= n, and 1 <= k <= n")
    if c < k:
        return 0.0
    return math.comb(c, k) / math.comb(n, k)
