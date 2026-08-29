import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.contract_extractor import extract_contract
from agents.source_analyzer import analyze_source
from agents.runtime_verifier import verify_contract
from agents.drift_detector import detect_drifts


def build_runtime_index(runtime_result):
    """
    Convert runtime verification results into a lookup table.

    Key:
        (endpoint, method)

    Value:
        runtime result
    """

    index = {}

    for result in runtime_result.get(
        "results",
        []
    ):

        key = (
            result.get("endpoint"),
            result.get("method")
        )

        index[key] = result

    return index


def normalize_type(value):
    """
    Normalize type names before comparison.
    """

    if value is None:
        return None

    value = str(value).strip().lower()

    aliases = {
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "str": "string",
        "list": "array",
        "dict": "object",
    }

    return aliases.get(
        value,
        value
    )


def find_runtime_field(
    runtime_result,
    field_name
):
    """
    Find a particular field in a runtime response.
    """

    fields = runtime_result.get(
        "fields",
        {}
    )

    return fields.get(
        field_name
    )


def calculate_confidence(
    static_actual,
    runtime_actual,
    expected
):
    """
    Calculate confidence using independent evidence.

    High:
        Static source and runtime both disagree
        with the documented contract.

    Medium:
        Only one independent source confirms
        the mismatch.

    Low:
        Evidence is incomplete or uncertain.
    """

    expected = normalize_type(
        expected
    )

    static_actual = normalize_type(
        static_actual
    )

    runtime_actual = normalize_type(
        runtime_actual
    )

    static_confirms = (
        static_actual is not None
        and static_actual != "unknown"
        and static_actual != expected
    )

    runtime_confirms = (
        runtime_actual is not None
        and runtime_actual != "unknown"
        and runtime_actual != expected
    )

    if (
        static_confirms
        and runtime_confirms
        and static_actual == runtime_actual
    ):
        return "high"

    if static_confirms or runtime_confirms:
        return "medium"

    return "low"


def enrich_drift(
    drift,
    runtime_index,
    source
):
    """
    Add runtime evidence and confidence
    to a deterministic drift candidate.
    """

    endpoint = drift.get(
        "endpoint"
    )

    method = drift.get(
        "method"
    )

    field = drift.get(
        "field_or_parameter"
    )

    expected = drift.get(
        "expected"
    )

    actual = drift.get(
        "actual"
    )

    runtime_result = runtime_index.get(
        (
            endpoint,
            method
        )
    )

    runtime_field = None

    if runtime_result is not None:

        runtime_field = find_runtime_field(
            runtime_result,
            field
        )

    runtime_type = None
    runtime_value = None

    if runtime_field is not None:

        runtime_type = runtime_field.get(
            "type"
        )

        runtime_value = runtime_field.get(
            "value"
        )

    confidence = calculate_confidence(
        actual,
        runtime_type,
        expected
    )

    enriched = dict(drift)

    enriched[
        "confidence"
    ] = confidence

    enriched[
        "evidence"
    ] = {
        "contract": expected,
        "source": actual,
        "runtime": runtime_type,
        "runtime_value": runtime_value,
    }

    return enriched


def fuse_evidence(
    openapi_path,
    source_path,
    base_url="http://127.0.0.1:5000"
):
    """
    Complete evidence-fusion pipeline.

    Pipeline:

        OpenAPI
            ↓
        Contract Extractor
            ↓
        Contract

        Source Code
            ↓
        Source Analyzer
            ↓
        Static Evidence

        Running API
            ↓
        Runtime Verifier
            ↓
        Runtime Evidence

        Contract + Source
            ↓
        Drift Detector
            ↓
        Candidates

        Candidates + Runtime Evidence
            ↓
        Evidence Fusion
            ↓
        High-confidence findings
    """

    # --------------------------------------------------
    # 1. Extract contract
    # --------------------------------------------------

    contract = extract_contract(
        openapi_path
    )

    # --------------------------------------------------
    # 2. Analyze source
    # --------------------------------------------------

    source = analyze_source(
        source_path
    )

    # --------------------------------------------------
    # 3. Detect static drifts
    # --------------------------------------------------

    static_result = detect_drifts(
        openapi_path,
        source_path
    )

    static_drifts = static_result.get(
        "drifts",
        []
    )

    # --------------------------------------------------
    # 4. Verify runtime behavior
    # --------------------------------------------------

    runtime = verify_contract(
        contract,
        base_url
    )

    runtime_index = build_runtime_index(
        runtime
    )

    # --------------------------------------------------
    # 5. Fuse evidence
    # --------------------------------------------------

    final_drifts = []

    for drift in static_drifts:

        enriched = enrich_drift(
            drift,
            runtime_index,
            source
        )

        final_drifts.append(
            enriched
        )

    # --------------------------------------------------
    # 6. Build final result
    # --------------------------------------------------

    return {
        "drifts": final_drifts,

        "summary": {
            "total_candidates":
                len(static_drifts),

            "high_confidence":
                sum(
                    1
                    for drift
                    in final_drifts
                    if drift.get(
                        "confidence"
                    ) == "high"
                ),

            "medium_confidence":
                sum(
                    1
                    for drift
                    in final_drifts
                    if drift.get(
                        "confidence"
                    ) == "medium"
                ),

            "low_confidence":
                sum(
                    1
                    for drift
                    in final_drifts
                    if drift.get(
                        "confidence"
                    ) == "low"
                ),
        },

        "contract": contract,

        "source": source,

        "runtime": runtime,
    }


if __name__ == "__main__":

    print(
        "Running evidence fusion..."
    )

    result = fuse_evidence(
        "benchmark/case01/openapi.yaml",
        "benchmark/case01/app.py"
    )

    print()

    print(
        "===== FINAL DRIFT REPORT ====="
    )

    print()

    print(
        json.dumps(
            result,
            indent=2
        )
    )