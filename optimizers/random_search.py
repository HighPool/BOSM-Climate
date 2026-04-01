from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class RandomSearchResult:
    X_hist: np.ndarray
    y_hist: np.ndarray
    best_hist: np.ndarray
    best_x: np.ndarray
    best_y: float
    n_evals: int
    seed: int


def sample_uniform(lb: np.ndarray, ub: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """
    Vygeneruje jeden náhodný bod rovnomerne v intervale <lb, ub>.
    """
    return lb + rng.random(lb.shape) * (ub - lb)


def run_random_search(problem, budget: int, seed: int = 0) -> RandomSearchResult:
    """
    Jeden beh random search.

    Očakáva, že problem má:
        - problem.dim
        - problem.lb
        - problem.ub
        - problem.evaluate(x)
    a že ide o minimalizačný problém.
    """
    rng = np.random.default_rng(seed)

    lb = np.asarray(problem.lb, dtype=float)
    ub = np.asarray(problem.ub, dtype=float)
    dim = int(problem.dim)

    if lb.shape != (dim,) or ub.shape != (dim,):
        raise ValueError("lb a ub musia mať tvar (dim,)")

    X_hist = np.zeros((budget, dim), dtype=float)
    y_hist = np.zeros(budget, dtype=float)
    best_hist = np.zeros(budget, dtype=float)

    best_y = np.inf
    best_x: Optional[np.ndarray] = None

    for k in range(budget):
        x = sample_uniform(lb, ub, rng)
        y = float(problem.evaluate(x))

        X_hist[k] = x
        y_hist[k] = y

        if y < best_y:
            best_y = y
            best_x = x.copy()

        best_hist[k] = best_y

    if best_x is None:
        raise RuntimeError("Random search nenašiel žiadne riešenie.")

    return RandomSearchResult(
        X_hist=X_hist,
        y_hist=y_hist,
        best_hist=best_hist,
        best_x=best_x,
        best_y=best_y,
        n_evals=budget,
        seed=seed,
    )