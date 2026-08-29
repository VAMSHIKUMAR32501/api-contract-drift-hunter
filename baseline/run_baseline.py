import json
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from baseline.baseline import analyze_case
from evaluator.evaluator import evaluate_case


RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def run_all_cases():
    results = []

    for case_number in range(1, 16):
        case_id = f"case{case_number:02d}"
        case_path = (
            PROJECT_ROOT
            / "benchmark"
            / case_id
        )

        print("\n" + "=" * 60)
        print(f"Running baseline: {case_id}")
        print("=" * 60)

        try:
            # Run the baseline model
            baseline_output = analyze_case(
                str(case_path)
            )

            # Evaluate the model output
            evaluation = evaluate_case(
                case_number,
                baseline_output
            )

            result = {
                "case_id": case_id,
                "baseline_output": baseline_output,
                "evaluation": evaluation
            }

            results.append(result)

            print("\nEvaluation:")
            print(
                json.dumps(
                    evaluation,
                    indent=2
                )
            )

        except Exception as e:
            print(f"\nERROR in {case_id}: {e}")

            results.append({
                "case_id": case_id,
                "error": str(e)
            })

    output_file = (
        RESULTS_DIR
        / "baseline_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            results,
            f,
            indent=2
        )

    print("\n" + "=" * 60)
    print("BASELINE RUN COMPLETE")
    print("=" * 60)

    print(f"\nResults saved to:")
    print(output_file)


if __name__ == "__main__":
    run_all_cases()