#!/usr/bin/env python3
"""
Driver for the real (non-synthetic-scope) GA experiment on the G200_*.txt
dataset: pop=20, max_generations=3000, twin removal every 50 generations,
random restart every 100, one run per replicate file - matching GA.java's
actual per-file protocol (minus the 20-iterations-per-file repeat, reduced
to 1 for runtime).

Resumable: if experiment_results.json already has entries for some files
(e.g. from a run that was interrupted), those files are skipped and their
results kept; only the remaining files are actually run. Safe to re-run
after any interruption - it will not redo completed files.
"""
import sys
import time
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
from egagp import EGAGP  # noqa: E402

DATA_DIR = REPO / "data"
LOG_PATH = REPO / "experiment_log.txt"
RESULTS_PATH = REPO / "experiment_results.json"


def main():
    egagp = EGAGP(data_dir=str(DATA_DIR), population_size=20, iterations=1, max_generations=3000)

    data_files = sorted(DATA_DIR.glob("G200_*.txt"))

    results = []
    if RESULTS_PATH.exists():
        with open(RESULTS_PATH) as rf:
            results = json.load(rf)
    done_files = {r["file"] for r in results}

    remaining = [f for f in data_files if f.name not in done_files]
    overall_start = time.time()

    with open(LOG_PATH, "a") as log:
        def emit(msg):
            print(msg, flush=True)
            log.write(msg + "\n")
            log.flush()

        if done_files:
            emit(f"Resuming: {len(done_files)}/{len(data_files)} files already done "
                 f"({sorted(done_files)}), {len(remaining)} remaining")
        else:
            emit(f"Starting experiment: {len(data_files)} files, pop=20, max_generations=3000, 1 run/file")

        for f in remaining:
            t0 = time.time()
            fitness, graph_cut = egagp.run_single_iteration(str(f))
            elapsed = time.time() - t0
            results.append({
                "file": f.name,
                "fitness": fitness,
                "graph_cut_cost": graph_cut,
                "elapsed_s": elapsed,
            })
            emit(f"{f.name}: graph_cut={graph_cut:.2f} fitness={fitness:.2f} "
                 f"elapsed={elapsed:.1f}s total_elapsed={time.time()-overall_start:.1f}s")
            with open(RESULTS_PATH, "w") as rf:
                json.dump(results, rf, indent=2)

        if len(results) == len(data_files):
            avg_total = sum(r["graph_cut_cost"] for r in results) / len(results)
            min_total = min(r["graph_cut_cost"] for r in results)
            emit("")
            emit(f"Avg graph cut cost: {avg_total:.2f}")
            emit(f"Min graph cut cost: {min_total:.2f}")
            emit("DONE")


if __name__ == "__main__":
    main()
