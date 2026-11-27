"""Multiple-testing correction."""
from __future__ import annotations


def benjamini_hochberg(ps: list[float]) -> list[float]:
    """Benjamini-Hochberg q-values, in the input order."""
    n = len(ps)
    order = sorted(range(n), key=lambda i: ps[i])
    q = [0.0] * n
    running = 1.0
    for rank, i in reversed(list(enumerate(order, start=1))):
        running = min(running, ps[i] * n / rank)
        q[i] = running
    return q
