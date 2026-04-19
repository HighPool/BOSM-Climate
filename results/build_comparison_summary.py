from __future__ import annotations
import csv
import json
from pathlib import Path

"""
Vytvorenie globálneho porovnania experimentálnych výsledkov každého algoritmu
- načíta summary JSON súbory jednotlivých metód
- z každého vytiahne globálne agregované metriky
- spojí ich do jednej porovnávacej tabuľky
- a uloží ju do JSON aj CSV formátu

Výstup slúži na porovnanie celkovej výkonnosti algoritmov na celej sade úloh LAQN
"""

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_row(label: str, payload: dict, source_path: Path) -> dict:
    config = payload.get("config", {})
    summary = payload.get("summary", {})

    return {
        "algorithm_name": config.get("algorithm_name", label),
        "source_file": str(source_path),

        "problem_dir": config.get("problem_dir", ""),
        "budget": config.get("budget", ""),
        "n_runs": config.get("n_runs", ""),
        "counting_mode": config.get("counting_mode", ""),

        "n_problems": summary.get("n_problems", ""),

        "mean_deviation": summary.get("mean_deviation", ""),
        "median_deviation": summary.get("median_deviation", ""),
        "std_deviation": summary.get("std_deviation", ""),

        "success_rate": summary.get("success_rate", ""),
        "mean_best_y": summary.get("mean_best_y", ""),
        "mean_evals_to_f_best": summary.get("mean_evals_to_f_best", ""),

        "mean_total_time": summary.get("mean_total_time", ""),
        "mean_unique_eval_count": summary.get("mean_unique_eval_count", ""),
        "mean_call_count": summary.get("mean_call_count", ""),

        "batch_total_time_seconds": summary.get("batch_total_time_seconds", ""),
        "batch_total_time_minutes": summary.get("batch_total_time_minutes", ""),
        "mean_time_per_problem": summary.get("mean_time_per_problem", ""),

        "min_curve_length": summary.get("min_curve_length", ""),
    }


def main():
    candidate_files = [
        ("TuRBO", Path("results/final/turbo/turbo_summary_2015_budget500_runs20.json")),
        ("RandomSearch", Path("results/final/random_search/random_search_summary_2015_budget500_runs20.json")),
        ("PyBADS", Path("results/final/pybads/pybads_summary_2015_budget500_runs20.json")),
    ]

    rows = []

    for label, path in candidate_files:
        if not path.exists():
            print(f"SKIP: {path} neexistuje")
            continue

        payload = load_json(path)
        row = extract_row(label, payload, path)
        rows.append(row)

    if not rows:
        raise FileNotFoundError("Nenašiel sa žiadny summary JSON súbor na porovnanie.")

    out_json = Path("results/comparison_summary.json")
    out_csv = Path("results/comparison_summary.csv")

    payload = {
        "rows": rows
    }

    with out_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    fieldnames = list(rows[0].keys())
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved JSON: {out_json}")
    print(f"Saved CSV:  {out_csv}")

    # Terminálový výpis hlavných globálnych metrík
    print("\n=== COMPARISON SUMMARY ===")
    for row in rows:
        print(
            f"{row['algorithm_name']} | "
            f"success_rate={row['success_rate']} | "
            f"mean_deviation={row['mean_deviation']} | "
            f"mean_total_time={row['mean_total_time']} | "
            f"batch_total_time_minutes={row['batch_total_time_minutes']}"
        )


if __name__ == "__main__":
    main()