"""Rerun the analysis in order, from the stacked panels to the figures, stopping at the first failure.

Reads:  the fetched data under panel/ and events/ (see the README for how to get it)
Writes: the result CSVs in results/, slides/fig/09, 12 to 26 and t1 to t9, and one log per step in
        logs/run_all/ (run.log lists each step as it finishes)
Run:    python3 run_all.py                       (the whole chain, about an hour)
        python3 run_all.py --list                (print the steps and stop)
        python3 run_all.py --from forecast/prediction_test.py   (resume at a step)

Not run here: fetching data (data/harvest_hs10.py, events/harvest_adcvd.py and the other
download and parsing scripts), and the frozen forecast. frozen_forecast.py must never be rerun;
frozen_forecast_check.py is run by hand once the outcome months are released.
"""
import os
import subprocess
import sys
import time

STEPS = [
    "measure/adcvd_stacked.py",
    "measure/adcvd_stacked_qty.py",
    "report1/adcvd_analysis.py",
    "events/itc_check.py",
    "events/itc_audit.py",
    "measure/itc_compare.py",
    "measure/recovery_benchmark.py --fall 0.1",
    "measure/recovery_benchmark.py --fall 0.3",
    "measure/recovery_benchmark.py --fall 0.2",  # the main threshold; kept last as in earlier runs
    "measure/recovery_by_final_stage.py",
    "measure/stakes_check.py",
    "measure/build_decision_stacks.py",
    "forecast/prediction_test.py",
    "forecast/prediction_stage2.py",
    "forecast/prediction_landmark.py",
    "forecast/calibrated_lookup.py",
    "forecast/decision_value.py",
    "forecast/review_queue.py",
    "forecast/review_queue_curves.py",
    "forecast/feature_ladder.py",
    "forecast/model_explain.py",
    "forecast/model_calibration.py",
    "forecast/model_recalibration.py",
    "forecast/model_family_check.py",
    "section301/sec301_benchmark.py",
    "section301/sec301_transfer_test.py",
    "slides/fig_stacked.py",
    "slides/fig_sankey.py",
    "slides/fig_funnel.py",
    "slides/fig_taiwan_example.py",
    "slides/fig_talk.py",  # the Presentation 2 v3 talk figures
]
LOGS = "logs/run_all"

os.chdir(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
if "--list" in args:
    print("\n".join(STEPS))
    sys.exit(0)
start = 0
if "--from" in args:
    first = args[args.index("--from") + 1]
    start = next(i for i, s in enumerate(STEPS) if s == first or s.split()[0] == first)

os.makedirs(LOGS, exist_ok=True)
with open(f"{LOGS}/run.log", "a" if start else "w") as run_log:
    for step in STEPS[start:]:
        name = step.replace("/", "_").replace(" ", "_").replace(".py", "")
        t0 = time.time()
        print(f"{time.strftime('%H:%M:%S')}  {step}", flush=True)
        with open(f"{LOGS}/{name}.log", "w") as log:
            code = subprocess.run([sys.executable, *step.split()], stdout=log,
                                  stderr=subprocess.STDOUT).returncode
        if code != 0:
            run_log.write(f"FAILED {step}\n")
            sys.exit(f"{step} failed; see {LOGS}/{name}.log")
        run_log.write(f"done {step} {time.strftime('%H:%M:%S')} ({time.time() - t0:.0f} s)\n")
        run_log.flush()
    run_log.write("ALL DONE\n")
print("all steps done")
