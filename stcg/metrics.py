"""Agreement and detection metrics. Pure functions, no dependencies."""

import math
from itertools import combinations

LABELS = (False, True)  # fine, overspecified


def cohen_kappa(a: list, b: list, labels=LABELS) -> float | None:
    """Cohen's kappa (nominal) between two raters."""
    n = len(a)
    if n == 0:
        return None
    p_o = sum(x == y for x, y in zip(a, b)) / n
    p_e = sum((a.count(lab) / n) * (b.count(lab) / n) for lab in labels)
    return None if p_e == 1 else (p_o - p_e) / (1 - p_e)


def fleiss_kappa(ratings: list[list], labels=LABELS) -> float | None:
    """Fleiss' kappa (nominal) for items each rated by the same number of raters."""
    ratings = [r for r in ratings if r]
    if not ratings or len({len(r) for r in ratings}) != 1 or len(ratings[0]) < 2:
        return None
    n_items, n_raters = len(ratings), len(ratings[0])
    counts = [[r.count(lab) for lab in labels] for r in ratings]
    p_j = [sum(c[j] for c in counts) / (n_items * n_raters) for j in range(len(labels))]
    p_i = [(sum(x * x for x in c) - n_raters) / (n_raters * (n_raters - 1)) for c in counts]
    p_bar, p_e = sum(p_i) / n_items, sum(p * p for p in p_j)
    return None if p_e == 1 else (p_bar - p_e) / (1 - p_e)


def pairwise_kappas(by_judge: dict[str, dict[str, bool]]) -> dict[str, dict]:
    """Cohen's kappa and raw agreement for every judge pair, over the tasks both judged."""
    out = {}
    for j1, j2 in combinations(sorted(by_judge), 2):
        common = sorted(set(by_judge[j1]) & set(by_judge[j2]))
        a = [by_judge[j1][t] for t in common]
        b = [by_judge[j2][t] for t in common]
        out[f"{j1}~{j2}"] = {
            "n": len(common),
            "kappa": cohen_kappa(a, b),
            "agree": sum(x == y for x, y in zip(a, b)) / len(common) if common else None,
        }
    return out


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n == 0:
        return None
    p = k / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, center - half), min(1.0, center + half))


def rate(k: int, n: int) -> dict:
    return {"k": k, "n": n, "rate": k / n if n else None, "ci95": wilson(k, n)}
