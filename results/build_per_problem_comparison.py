from __future__ import annotations
import csv
import json
from pathlib import Path

"""
Vytvorenie porovnania výsledkov po jednotlivých inštanciách problémov
- načíta summary JSON súbory jednotlivých metód
- z ich časti `results` vytvorí index podľa identifikátora problému
- spojí metriky viacerých metód do jedného riadku pre každú úlohu
- a uloží výsledok do JSON aj CSV formátu

Výstup slúži na detailné porovnanie správanaia algoritmov na konkrétnych inštanciách problémov
"""

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def index_results_by_identifier(payload: dict) -> dict:
    results = payload.get("results", [])
    indexed = {}

    for row in results:
        identifier = row.get("identifier")
        if identifier:
            indexed[identifier] = row

    return indexed

def main():
    candidate_files = [
        ("TuRBO", Path("results/final/turbo/turbo_summary_2015_budget500_runs20.json")),
        ("RandomSearch", Path("results/final/random_search/random_search_summary_2015_budget500_runs20.json")),
        ("PyBADS", Path("results/final/pybads/pybads_summary_2015_budget500_runs20.json")),
    ]

    loaded = {}

    for label, path in candidate_files:
        if not path.exists():
            print(f"SKIP: {path} neexistuje")
            continue

        payload = load_json(path)
        loaded[label] = index_results_by_identifier(payload)

    if not loaded:
        raise FileNotFoundError("Nenašiel sa žiadny summary JSON súbor.")

    all_identifiers = sorted(
        set().union(*[set(problem_map.keys()) for problem_map in loaded.values()])
    )

    rows = []

    for identifier in all_identifiers:
        row = {"identifier": identifier}

        for algorithm_name, problem_map in loaded.items():
            result = problem_map.get(identifier, {})

            prefix = algorithm_name.lower()

            row[f"{prefix}_mean_deviation"] = result.get("mean_deviation", "")
            row[f"{prefix}_median_deviation"] = result.get("median_deviation", "")
            row[f"{prefix}_std_deviation"] = result.get("std_deviation", "")

            row[f"{prefix}_success_rate"] = result.get("success_rate", "")
            row[f"{prefix}_mean_best_y"] = result.get("mean_best_y", "")
            row[f"{prefix}_mean_evals_to_f_best"] = result.get("mean_evals_to_f_best", "")
            row[f"{prefix}_mean_total_time"] = result.get("mean_total_time", "")
            row[f"{prefix}_mean_unique_eval_count"] = result.get("mean_unique_eval_count", "")
            row[f"{prefix}_mean_call_count"] = result.get("mean_call_count", "")
            row[f"{prefix}_true_maximum"] = result.get("true_maximum", "")

        rows.append(row)

    out_json = Path("results/per_problem_comparison.json")
    out_csv = Path("results/per_problem_comparison.csv")

    with out_json.open("w", encoding="utf-8") as f:
        json.dump({"rows": rows}, f, indent=2, ensure_ascii=False)

    fieldnames = list(rows[0].keys()) if rows else ["identifier"]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved JSON: {out_json}")
    print(f"Saved CSV:  {out_csv}")
    print(f"Rows: {len(rows)}")


if __name__ == "__main__":
    main()