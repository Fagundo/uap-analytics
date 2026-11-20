"""Compare a freshly computed result with the committed one, value by value."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

IGNORED_KEYS = frozenset({"manifest"})   # run time, commit and input hashes change on every run


@dataclass(frozen=True)
class Difference:
    path: str
    expected: Any
    actual: Any

    def line(self) -> str:
        return f"{self.path}: committed {self.expected!r}, now {self.actual!r}"


class ResultComparer:
    """Walks two JSON-like trees. Numbers match within rel_tol (relative) or abs_tol (absolute, for values near
    zero such as tiny p-values); NaN matches NaN; strings, booleans and None must be equal; keys must match."""

    def __init__(self, rel_tol: float = 1e-6, abs_tol: float = 1e-12, ignored: frozenset[str] = IGNORED_KEYS) -> None:
        self.rel_tol = rel_tol
        self.abs_tol = abs_tol
        self.ignored = ignored

    def compare(self, expected: Any, actual: Any) -> list[Difference]:
        out: list[Difference] = []
        self._walk(expected, actual, "", out)
        return out

    def _walk(self, a: Any, b: Any, path: str, out: list[Difference]) -> None:
        if isinstance(a, dict) and isinstance(b, dict):
            for key in sorted(set(a) | set(b), key=str):
                if key in self.ignored:
                    continue
                sub = f"{path}.{key}" if path else str(key)
                if key not in a or key not in b:
                    out.append(Difference(sub, a.get(key, "<missing>"), b.get(key, "<missing>")))
                else:
                    self._walk(a[key], b[key], sub, out)
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                out.append(Difference(f"{path}[len]", len(a), len(b)))
                return
            for i, (x, y) in enumerate(zip(a, b)):
                self._walk(x, y, f"{path}[{i}]", out)
        elif self._is_number(a) and self._is_number(b):
            if not self._close(float(a), float(b)):
                out.append(Difference(path, a, b))
        elif a != b:
            out.append(Difference(path, a, b))

    @staticmethod
    def _is_number(x: Any) -> bool:
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    def _close(self, x: float, y: float) -> bool:
        if math.isnan(x) or math.isnan(y):
            return math.isnan(x) and math.isnan(y)
        return math.isclose(x, y, rel_tol=self.rel_tol, abs_tol=self.abs_tol)
