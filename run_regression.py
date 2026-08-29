import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "results"

RESULTS_DIR.mkdir(exist_ok=True)


# ============================================================
# CASE -> FLASK PORT
# ============================================================

CASE_PORTS = {
    1: 5000,
    2: 5001,
    3: 5002,
    4: 5003,
    5: 5004,
    6: 5005,
    7: 5006,
    8: 5007,
    9: 5008,
    10: 5009,
    11: 5010,
    12: 5011,
    13: 5012,
    14: 5013,
    15: 5014,
}


# ============================================================
# RUN ONE CASE
# ============================================================

def run_case(case_number):

    case_id = f"case{case_number:02d}"

    port = CASE_PORTS[case_number]

    base_url = (
        f"http://127.0.0.1:{port}"
    )

    print()
    print("=" * 60)
    print(f"RUNNING {case_id}")
    print("=" * 60)

    print(
        f"Base URL: {base_url}"
    )

    # --------------------------------------------------------
    # Run pipeline
    # --------------------------------------------------------

    result = subprocess.run(
        [
            sys.executable,
            "agents/pipeline.py",
            case_id,
            base_url
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    # --------------------------------------------------------
    # Pipeline error
    # --------------------------------------------------------

    if result.returncode != 0:

        print(result.stdout)
        print(result.stderr)

        return {
            "case_id": case_id,
            "status": "ERROR",
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0
        }

    # --------------------------------------------------------
    # Print pipeline output
    # --------------------------------------------------------

    print(result.stdout)

    # --------------------------------------------------------
    # Result file
    # --------------------------------------------------------

    result_file = (
        RESULTS_DIR
        / f"{case_id}_pipeline_results.json"
    )

    if not result_file.exists():

        print(
            f"Missing result file: {result_file}"
        )

        return {
            "case_id": case_id,
            "status": "MISSING_RESULT",
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0
        }

    # --------------------------------------------------------
    # Load result
    # --------------------------------------------------------

    try:

        with open(
            result_file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except Exception as exc:

        print(
            f"Could not read {result_file}: {exc}"
        )

        return {
            "case_id": case_id,
            "status": "INVALID_RESULT",
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0
        }

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    evaluation = data.get(
        "evaluation",
        data.get(
            "final_evaluation",
            {}
        )
    )

    precision = float(
        evaluation.get(
            "precision",
            0.0
        )
    )

    recall = float(
        evaluation.get(
            "recall",
            0.0
        )
    )

    f1 = float(
        evaluation.get(
            "f1",
            0.0
        )
    )

    # --------------------------------------------------------
    # PASS / FAIL
    # --------------------------------------------------------

    passed = (
        precision == 1.0
        and recall == 1.0
        and f1 == 1.0
    )

    return {
        "case_id": case_id,
        "status":
            "PASS"
            if passed
            else "FAIL",
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("API CONTRACT DRIFT HUNTER")
    print("15-CASE REGRESSION")
    print("=" * 60)

    results = []

    # --------------------------------------------------------
    # Run all cases
    # --------------------------------------------------------

    for case_number in range(1, 16):

        result = run_case(
            case_number
        )

        results.append(
            result
        )

        print(
            f"{result['case_id']}: "
            f"{result['status']} | "
            f"P={result['precision']:.3f} | "
            f"R={result['recall']:.3f} | "
            f"F1={result['f1']:.3f}"
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    total_cases = len(results)

    passed = sum(
        result["status"] == "PASS"
        for result in results
    )

    failed = (
        total_cases - passed
    )

    average_precision = (
        sum(
            result["precision"]
            for result in results
        )
        / total_cases
    )

    average_recall = (
        sum(
            result["recall"]
            for result in results
        )
        / total_cases
    )

    average_f1 = (
        sum(
            result["f1"]
            for result in results
        )
        / total_cases
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("REGRESSION SUMMARY")
    print("=" * 60)

    print(
        f"Cases tested : {total_cases}"
    )

    print(
        f"Cases passed : {passed}"
    )

    print(
        f"Cases failed : {failed}"
    )

    print()

    print(
        f"Average Precision : "
        f"{average_precision:.3f}"
    )

    print(
        f"Average Recall    : "
        f"{average_recall:.3f}"
    )

    print(
        f"Average F1        : "
        f"{average_f1:.3f}"
    )

    print()

    # --------------------------------------------------------
    # Failed cases
    # --------------------------------------------------------

    if failed == 0:

        print(
            "ALL 15 CASES PASSED"
        )

    else:

        print(
            "SOME CASES FAILED"
        )

        print()
        print(
            "Failed cases:"
        )

        for result in results:

            if result["status"] != "PASS":

                print(
                    f"  - {result['case_id']}"
                )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Save summary
    # --------------------------------------------------------

    summary_file = (
        RESULTS_DIR
        / "regression_summary.json"
    )

    with open(
        summary_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "total_cases":
                    total_cases,

                "passed":
                    passed,

                "failed":
                    failed,

                "average_precision":
                    average_precision,

                "average_recall":
                    average_recall,

                "average_f1":
                    average_f1,

                "cases":
                    results
            },
            file,
            indent=2
        )

    print()

    print(
        f"Summary saved to: "
        f"{summary_file}"
    )

    return (
        0
        if failed == 0
        else 1
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )