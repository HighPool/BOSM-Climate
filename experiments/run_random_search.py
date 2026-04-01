import numpy as np

from problems.problem_wrapper import SphereProblem
from optimizers.random_search import run_random_search
from utils.metrics import summarize_runs


def main():
    problem = SphereProblem(dim=2)

    budget = 30
    n_runs = 10

    all_best_final = np.zeros(n_runs, dtype=float)
    all_best_curves = np.zeros((n_runs, budget), dtype=float)

    for run_idx in range(n_runs):
        result = run_random_search(problem=problem, budget=budget, seed=run_idx)

        all_best_final[run_idx] = result.best_y
        all_best_curves[run_idx] = result.best_hist

    summary = summarize_runs(all_best_final, all_best_curves)

    print("Mean final best:", summary["best_final_mean"])
    print("Median final best:", summary["best_final_median"])
    print("Std final best:", summary["best_final_std"])
    print("Mean convergence curve:", summary["mean_curve"])
    print("Median convergence curve:", summary["median_curve"])


if __name__ == "__main__":
    main()