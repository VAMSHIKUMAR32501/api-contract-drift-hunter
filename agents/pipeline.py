import json
import sys
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# AGENT IMPORTS
# ============================================================

from evaluator.evaluator import (
    evaluate_case
)

from agents.contract_extractor import (
    extract_contract
)

from agents.source_analyzer import (
    analyze_source
)

from agents.drift_detector import (
    detect_drifts
)

from agents.request_generator import (
    generate_requests
)

from agents.runtime_verifier import (
    verify_contract
)

from agents.negative_test_generator import (
    generate_negative_tests_for_contract
)

from agents.negative_runtime_verifier import (
    verify_negative_tests
)

from agents.runtime_drift_detector import (
    detect_runtime_drifts
)

from agents.finding_normalizer import (
    normalize_result
)


# ============================================================
# DEFAULT CONFIGURATION
# ============================================================

DEFAULT_CASE = "case11"

DEFAULT_BASE_URL = "http://127.0.0.1:5010"

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
)

RESULTS_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# CASE PATHS
# ============================================================

def load_case_paths(case_id):
    """
    Return important paths for a benchmark case.
    """

    case_path = (
        PROJECT_ROOT
        / "benchmark"
        / case_id
    )

    openapi_path = (
        case_path
        / "openapi.yaml"
    )

    source_path = (
        case_path
        / "app.py"
    )

    expected_path = (
        case_path
        / "expected.json"
    )

    return (
        case_path,
        openapi_path,
        source_path,
        expected_path
    )


# ============================================================
# EXPECTED RESULT
# ============================================================

def load_expected(expected_path):
    """
    Load expected.json for benchmark reporting.

    IMPORTANT:
    This is never passed into the detection agents.
    """

    if not expected_path.exists():
        return None

    try:

        with open(
            expected_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:
        return None


# ============================================================
# EVALUATOR FORMAT
# ============================================================

def convert_drifts_to_evaluator_format(
    normalized_result
):
    """
    Convert our normalized drift structure into
    the format expected by evaluator.py.
    """

    if not isinstance(
        normalized_result,
        dict
    ):
        return {
            "issues": []
        }

    drifts = normalized_result.get(
        "drifts",
        []
    )

    if not isinstance(
        drifts,
        list
    ):
        return {
            "issues": []
        }

    issues = []

    for drift in drifts:

        if not isinstance(
            drift,
            dict
        ):
            continue

        issues.append({

            "endpoint":
                drift.get(
                    "endpoint",
                    ""
                ),

            "issue_type":
                drift.get(
                    "issue_type",
                    ""
                ),

            "field_or_parameter":
                drift.get(
                    "field_or_parameter",
                    ""
                ),

            "expected":
                drift.get(
                    "expected",
                    ""
                ),

            "actual":
                drift.get(
                    "actual",
                    ""
                )
        })

    return {
        "issues": issues
    }


# ============================================================
# MERGE STATIC + RUNTIME DRIFTS
# ============================================================

def merge_drifts(
    static_drifts,
    runtime_drifts
):
    """
    Combine deterministic static findings and
    runtime findings.

    Exact duplicates are removed.

    We deliberately keep distinct findings because
    static and runtime evidence can reveal different
    problems.
    """

    if not isinstance(
        static_drifts,
        list
    ):
        static_drifts = []

    if not isinstance(
        runtime_drifts,
        list
    ):
        runtime_drifts = []

    combined = []

    seen = set()

    for drift in (
        static_drifts
        + runtime_drifts
    ):

        if not isinstance(
            drift,
            dict
        ):
            continue

        def make_hashable(value):

            if isinstance(
                value,
                dict
            ):
                return tuple(
                    sorted(
                        (
                            key,
                            make_hashable(
                                val
                            )
                        )
                        for key, val
                        in value.items()
                    )
                )

            if isinstance(
                value,
                list
            ):
                return tuple(
                    make_hashable(
                        item
                    )
                    for item in value
                )

            if isinstance(
                value,
                set
            ):
                return tuple(
                    sorted(
                        make_hashable(
                            item
                        )
                        for item in value
                    )
                )

            return value

        key = (
            make_hashable(
                drift.get(
                    "endpoint"
                )
            ),

            make_hashable(
                drift.get(
                    "method"
                )
            ),

            make_hashable(
                drift.get(
                    "issue_type"
                )
            ),

            make_hashable(
                drift.get(
                    "field_or_parameter"
                )
            ),

            make_hashable(
                drift.get(
                    "expected"
                )
            ),

            make_hashable(
                drift.get(
                    "actual"
                )
            ),
        )

        if key in seen:
            continue

        seen.add(key)

        combined.append(
            drift
        )

    return combined

# ============================================================
# SAVE RESULT
# ============================================================

def save_result(
    result,
    case_id
):
    """
    Save complete pipeline output.
    """

    output_file = (
        RESULTS_DIR
        / f"{case_id}_pipeline_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2
        )

    return output_file


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(
    case_id=DEFAULT_CASE,
    base_url=DEFAULT_BASE_URL
):

    (
        case_path,
        openapi_path,
        source_path,
        expected_path
    ) = load_case_paths(
        case_id
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    if not case_path.exists():

        raise FileNotFoundError(
            f"Case not found: {case_path}"
        )

    if not openapi_path.exists():

        raise FileNotFoundError(
            f"OpenAPI file not found: "
            f"{openapi_path}"
        )

    if not source_path.exists():

        raise FileNotFoundError(
            f"Source file not found: "
            f"{source_path}"
        )

    # ========================================================
    # STEP 1
    # CONTRACT EXTRACTION
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 1: CONTRACT EXTRACTION")
    print("=" * 60)

    contract = extract_contract(
        str(openapi_path)
    )

    print(
        "Endpoints extracted:",
        len(
            contract.get(
                "endpoints",
                []
            )
        )
    )

    # ========================================================
    # STEP 2
    # SOURCE ANALYSIS
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 2: SOURCE ANALYSIS")
    print("=" * 60)

    source = analyze_source(
        str(source_path)
    )

    print(
        "Routes analyzed:",
        len(
            source.get(
                "routes",
                []
            )
        )
    )

    # ========================================================
    # STEP 3
    # STATIC DRIFT DETECTION
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 3: STATIC DRIFT DETECTION")
    print("=" * 60)

    static_result = detect_drifts(
    str(openapi_path),
    str(source_path)
)

    if isinstance(
    static_result,
    dict
):
     static_drifts = static_result.get(
       "drifts",
        []
    )
    else:
      static_drifts = []

    if not isinstance(
    static_drifts,
    list
):
     static_drifts = []

    print(
    "Static drifts detected:",
    len(static_drifts)
)

    # ========================================================
    # STEP 4
    # REQUEST GENERATION
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 4: REQUEST GENERATION")
    print("=" * 60)

    requests = generate_requests(
        contract
    )

    print(
        "Requests generated:",
        len(requests)
    )

    # ========================================================
    # STEP 5
    # RUNTIME VERIFICATION
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 5: RUNTIME VERIFICATION")
    print("=" * 60)

    runtime_results = verify_contract(
        contract,
        base_url
    )

    print(
        "Runtime results:",
        len(
            runtime_results.get(
                "results",
                []
            )
        )
    )

    # ========================================================
    # STEP 6
    # NEGATIVE TEST GENERATION
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 6: NEGATIVE TEST GENERATION")
    print("=" * 60)

    negative_tests = (
        generate_negative_tests_for_contract(
            contract
        )
    )

    print(
        "Negative tests generated:",
        len(negative_tests)
    )

    # ========================================================
    # STEP 7
    # NEGATIVE RUNTIME VERIFICATION
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 7: NEGATIVE RUNTIME VERIFICATION")
    print("=" * 60)

    negative_runtime_results = (
        verify_negative_tests(
            contract,
            base_url
        )
    )

    print(
        "Negative runtime results:",
        len(
            negative_runtime_results.get(
                "results",
                []
            )
        )
    )


    # ========================================================
    # STEP 8
    # RUNTIME DRIFT DETECTION
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 8: RUNTIME DRIFT DETECTION")
    print("=" * 60)

    runtime_drifts = detect_runtime_drifts(
        contract,
        negative_runtime_results,
        source
    )

    if not isinstance(
        runtime_drifts,
        list
    ):
        runtime_drifts = []

    print(
        "Runtime drifts detected:",
        len(runtime_drifts)
    )

    # ========================================================
    # STEP 9
    # MERGE STATIC + RUNTIME
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 9: MERGE DRIFT EVIDENCE")
    print("=" * 60)

    combined_drifts = merge_drifts(
        static_drifts,
        runtime_drifts
    )

    print(
        "Combined drifts:",
        len(combined_drifts)
    )

    # ========================================================
    # STEP 10
    # FINDING NORMALIZATION
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 10: FINDING NORMALIZATION")
    print("=" * 60)

    normalized_result = normalize_result(
        {
            "drifts":
                combined_drifts
        },
        source,
        contract
    )

    normalized_drifts = (
        normalized_result.get(
            "drifts",
            []
        )
    )

    print(
        "Normalized drifts:",
        len(normalized_drifts)
    )

    # ========================================================
    # STEP 11
    # EVALUATOR FORMAT
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 11: EVALUATOR FORMAT")
    print("=" * 60)

    evaluator_input = (
        convert_drifts_to_evaluator_format(
            normalized_result
        )
    )

    print(
        "Evaluator issues:",
        len(
            evaluator_input.get(
                "issues",
                []
            )
        )
    )

    # ========================================================
    # STEP 12
    # EVALUATION
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 12: EVALUATION")
    print("=" * 60)

    print()
    print("Evaluator input:")

    print(
        json.dumps(
            evaluator_input,
            indent=2
        )
    )

    try:

        case_number = int(
            case_id.replace(
                "case",
                ""
            )
        )

        evaluation = evaluate_case(
            case_number,
            json.dumps(
                evaluator_input
            )
        )

    except Exception as e:

        evaluation = {
            "case_id":
                case_id,

            "error":
                (
                    f"{type(e).__name__}: {e}"
                )
        }

    print()
    print("Evaluation result:")

    print(
        json.dumps(
            evaluation,
            indent=2
        )
    )

    # ========================================================
    # EXPECTED
    # ========================================================

    expected = load_expected(
        expected_path
    )

    # ========================================================
    # COMPLETE RESULT
    # ========================================================

    result = {

        "case_id":
            case_id,

        "base_url":
            base_url,

        "contract":
            contract,

        "source":
            source,

        "requests":
            requests,

        "runtime":
            runtime_results,

        "negative_tests":
            negative_tests,

        "negative_runtime":
            negative_runtime_results,

        "static_drifts":
            static_drifts,

        "runtime_drifts":
            runtime_drifts,

        "combined_drifts":
            combined_drifts,

        "normalized":
            normalized_result,

        "evaluator_input":
            evaluator_input,

        "evaluation":
            evaluation,

        "expected":
            expected
    }

    # ========================================================
    # SAVE
    # ========================================================

    output_file = save_result(
        result,
        case_id
    )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 60)
    print("FINAL DRIFT REPORT")
    print("=" * 60)

    print()

    print(
        json.dumps(
            normalized_result,
            indent=2
        )
    )

    # ========================================================
    # FINAL EVALUATION
    # ========================================================

    print()
    print("=" * 60)
    print("FINAL EVALUATION")
    print("=" * 60)

    print()

    print(
        json.dumps(
            evaluation,
            indent=2
        )
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    print()
    print("=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)

    print()

    print(
        "Results saved to:"
    )

    print(
        output_file
    )

    return result


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    case_id = DEFAULT_CASE

    base_url = DEFAULT_BASE_URL

    if len(sys.argv) >= 2:

        case_id = sys.argv[1]

    if len(sys.argv) >= 3:

        base_url = sys.argv[2]

    try:

        run_pipeline(
            case_id,
            base_url
        )

    except Exception as e:

        print()
        print("=" * 60)
        print("PIPELINE ERROR")
        print("=" * 60)

        print()

        print(
            f"{type(e).__name__}: {e}"
        )

        sys.exit(1)