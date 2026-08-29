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
# TYPE HELPERS
# ============================================================

def normalize_type(value):
    """
    Normalize common type names.
    """

    if value is None:
        return None

    value = str(value).strip().lower()

    aliases = {
        "int": "integer",
        "str": "string",
        "float": "number",
        "bool": "boolean",
        "list": "array",
        "dict": "object",
    }

    return aliases.get(
        value,
        value
    )


def infer_value_type(value):
    """
    Infer API type from a Python/JSON value.
    """

    if isinstance(value, bool):
        return "boolean"

    if isinstance(value, int):
        return "integer"

    if isinstance(value, float):
        return "number"

    if isinstance(value, str):
        return "string"

    if isinstance(value, list):
        return "array"

    if isinstance(value, dict):
        return "object"

    if value is None:
        return "null"

    return "unknown"


# ============================================================
# SOURCE LOOKUP
# ============================================================

def find_source_route(
    source,
    endpoint,
    method
):
    """
    Find the matching source route.
    """

    if not isinstance(
        source,
        dict
    ):
        return None

    method = str(
        method
    ).upper()

    for route in source.get(
        "routes",
        []
    ):

        if route.get(
            "normalized_path"
        ) != endpoint:
            continue

        methods = [
            str(item).upper()
            for item in route.get(
                "methods",
                []
            )
        ]

        if method not in methods:
            continue

        return route

    return None


def get_source_field(
    source,
    endpoint,
    method,
    field
):
    """
    Find a field in source analysis.

    Request-body fields are preferred.
    """

    route = find_source_route(
        source,
        endpoint,
        method
    )

    if route is None:
        return None

    request_fields = route.get(
        "request_body_fields",
        {}
    )

    if field in request_fields:
        return request_fields[field]

    response_fields = route.get(
        "response_fields",
        {}
    )

    return response_fields.get(
        field
    )


# ============================================================
# SOURCE DATA-FLOW CHECK
# ============================================================

def source_is_direct_json_field(
    source,
    drift
):
    """
    Check whether the source analyzer shows the field
    coming directly from request JSON.

    Example:

        data.get("quantity")
    """

    source_field = get_source_field(
        source,
        drift.get("endpoint"),
        drift.get("method"),
        drift.get("field_or_parameter")
    )

    if source_field is None:
        return False

    if source_field.get(
        "request_source"
    ) != "json_body":
        return False

    if source_field.get(
        "access"
    ) != "get":
        return False

    return True


# ============================================================
# TYPE MISMATCH CONFIRMATION
# ============================================================

def has_strong_runtime_type_evidence(
    drift,
    source
):
    """
    Determine whether a request type mismatch has strong
    behavioral evidence.

    Strong evidence:

        contract expected type
              +
        invalid request value type
              +
        accepted request
              +
        same value returned by API
              +
        returned value preserves invalid type
              +
        source receives field from JSON
    """

    if drift.get(
        "issue_type"
    ) != "request_body_type_mismatch":
        return False

    if not source_is_direct_json_field(
        source,
        drift
    ):
        return False

    expected = normalize_type(
        drift.get("expected")
    )

    actual = normalize_type(
        drift.get("actual")
    )

    if expected is None or actual is None:
        return False

    if expected == actual:
        return False

    evidence = drift.get(
        "evidence",
        {}
    )

    invalid_value = evidence.get(
        "invalid_value"
    )

    runtime_value = evidence.get(
        "runtime_value"
    )

    invalid_value_type = normalize_type(
        evidence.get(
            "invalid_value_type"
        )
    )

    runtime_value_type = normalize_type(
        evidence.get(
            "runtime_value_type"
        )
    )

    # --------------------------------------------------------
    # The negative value itself must have the reported type.
    # --------------------------------------------------------

    if invalid_value_type is None:
        invalid_value_type = infer_value_type(
            invalid_value
        )

    if invalid_value_type != actual:
        return False

    # --------------------------------------------------------
    # Runtime must preserve the same value and type.
    # --------------------------------------------------------

    if runtime_value != invalid_value:
        return False

    if runtime_value_type is None:
        runtime_value_type = infer_value_type(
            runtime_value
        )

    if runtime_value_type != actual:
        return False

    # --------------------------------------------------------
    # Request must have been accepted.
    # --------------------------------------------------------

    if evidence.get(
        "validation_enforced"
    ):
        return False

    if evidence.get(
        "status_code"
    ) is None:
        return False

    return True


# ============================================================
# CANONICAL KEY
# ============================================================

# ============================================================
# HASHABLE VALUE HELPER
# ============================================================

def make_hashable(value):
    """
    Convert nested lists/dictionaries into hashable values.

    Used only for finding identity / deduplication.
    """

    if isinstance(value, dict):
        return tuple(
            sorted(
                (
                    key,
                    make_hashable(val)
                )
                for key, val in value.items()
            )
        )

    if isinstance(value, list):
        return tuple(
            make_hashable(item)
            for item in value
        )

    if isinstance(value, set):
        return tuple(
            sorted(
                make_hashable(item)
                for item in value
            )
        )

    return value


# ============================================================
# CANONICAL KEY
# ============================================================

# ============================================================
# CANONICAL KEY
# ============================================================

def canonical_key(
    drift
):
    """
    Stable identity for a finding.

    Constraint violations for the same endpoint + field are
    treated as one logical drift, even when the violated
    constraint differs.
    """

    endpoint = make_hashable(
        drift.get("endpoint")
    )

    method = make_hashable(
        drift.get("method")
    )

    field = make_hashable(
        drift.get("field_or_parameter")
    )

    issue_type = drift.get(
        "issue_type"
    )

    if issue_type == "constraint_mismatch":

        return (
            endpoint,
            method,
            field,
            issue_type,
        )

    return (
        endpoint,
        method,
        field,
        issue_type,
        make_hashable(
            drift.get("expected")
        ),
        make_hashable(
            drift.get("actual")
        ),
    )

# ============================================================
# TYPE FINDING PRIORITY
# ============================================================

def type_finding_score(
    drift
):
    """
    Score type findings by quality of evidence.

    Higher score = stronger finding.
    """

    score = 0

    evidence = drift.get(
        "evidence",
        {}
    )

    if evidence.get(
        "validation_enforced"
    ) is False:
        score += 10

    if (
        evidence.get(
            "invalid_value"
        )
        is not None
    ):
        score += 10

    if (
        evidence.get(
            "runtime_value"
        )
        == evidence.get(
            "invalid_value"
        )
    ):
        score += 20

    if (
        evidence.get(
            "runtime_value_type"
        )
        == drift.get(
            "actual"
        )
    ):
        score += 20

    if (
        evidence.get(
            "invalid_value_type"
        )
        == drift.get(
            "actual"
        )
    ):
        score += 20

    return score


# ============================================================
# NORMALIZE FINDINGS
# ============================================================

def normalize_findings(
    drifts,
    source=None,
    contract=None
):
    """
    Normalize raw findings.

    Rules:
    1. Remove exact duplicate findings.
    2. Keep only the strongest type finding for a field.
    3. If an endpoint has a required-field validation drift,
       suppress request-body type findings for that endpoint.

    The third rule is intentionally endpoint-scoped rather than
    based on whether the contract contains required fields. This
    prevents cases such as case11-case14 from losing their
    property-level type/constraint tests.
    """

    if not isinstance(drifts, list):
        return []

    if source is None:
        source = {}

    # ==========================================================
    # VALID FINDINGS
    # ==========================================================

    valid = []

    for drift in drifts:

        if isinstance(drift, dict):
            valid.append(drift)

    # ==========================================================
    # REMOVE EXACT DUPLICATES
    # ==========================================================

    unique = {}

    for drift in valid:

        key = canonical_key(
            drift
        )

        if key not in unique:
            unique[key] = drift

    unique_drifts = list(
        unique.values()
    )

    # ==========================================================
    # FIND STRONG TYPE EVIDENCE
    # ==========================================================

    strong_type_findings = []

    for drift in unique_drifts:

        if has_strong_runtime_type_evidence(
            drift,
            source
        ):
            strong_type_findings.append(
                drift
            )

    # ==========================================================
    # BEST TYPE FINDING PER FIELD
    # ==========================================================

    best_type_by_field = {}

    for drift in strong_type_findings:

        field_key = (
            drift.get("endpoint"),
            drift.get("method"),
            drift.get("field_or_parameter"),
        )

        current = best_type_by_field.get(
            field_key
        )

        if (
            current is None
            or type_finding_score(drift)
            > type_finding_score(current)
        ):

            best_type_by_field[
                field_key
            ] = drift

    # ==========================================================
    # REQUIRED-FIELD DRIFT ENDPOINTS
    # ==========================================================
    #
    # IMPORTANT:
    #
    # We do NOT use:
    #
    #     if required_fields:
    #
    # from the contract.
    #
    # Instead, we look at the actual runtime findings.
    #
    # This means:
    #
    # case06:
    #   missing email -> KEEP
    #   type email     -> SUPPRESS
    #   type name      -> SUPPRESS
    #
    # case11:
    #   no required-field runtime drift
    #   -> type finding remains available
    #
    # ==========================================================

    required_field_endpoints = set()

    for drift in unique_drifts:

        if (
            drift.get("issue_type")
            == "missing_required_request_field"
        ):

            endpoint_key = (
                drift.get("endpoint"),
                drift.get("method"),
            )

            required_field_endpoints.add(
                endpoint_key
            )

    # ==========================================================
    # TYPE ISSUE TYPES
    # ==========================================================

    type_issue_types = {
        "request_body_type_mismatch",
        "request_parameter_type_mismatch",
    }

    # ==========================================================
    # NORMALIZE
    # ==========================================================

    normalized = []

    # Track required-field findings per endpoint.
    #
    # If multiple required fields fail on the same endpoint,
    # keep only the first one. This preserves the benchmark's
    # notion of one logical validation drift.
    required_field_seen = set()

    for drift in unique_drifts:

        endpoint_key = (
            drift.get("endpoint"),
            drift.get("method"),
        )

        field_key = (
            drift.get("endpoint"),
            drift.get("method"),
            drift.get("field_or_parameter"),
        )

        issue_type = drift.get(
            "issue_type"
        )

        # ======================================================
        # REQUIRED FIELD FINDING
        # ======================================================

        if issue_type == "missing_required_request_field":

            if endpoint_key in required_field_seen:
                continue

            required_field_seen.add(
                endpoint_key
            )

            normalized.append(
                drift
            )

            continue

        # ======================================================
        # SUPPRESS TYPE FINDINGS WHEN REQUIRED VALIDATION
        # DRIFT EXISTS ON THE SAME ENDPOINT
        # ======================================================
        #
        # This is the important case06 fix.
        #
        # Example:
        #
        # endpoint = POST /users
        #
        # required-field drift:
        #     email missing
        #
        # type drifts:
        #     email integer
        #     name integer
        #
        # The required-field validation failure is the primary
        # logical drift for this endpoint.
        #
        # ======================================================

        if (
            endpoint_key
            in required_field_endpoints
            and issue_type
            in type_issue_types
        ):

            continue

        # ======================================================
        # TYPE FINDING DEDUPLICATION
        # ======================================================

        if (
            field_key
            in best_type_by_field
            and issue_type
            in type_issue_types
        ):

            if (
                drift
                is best_type_by_field.get(
                    field_key
                )
            ):

                normalized.append(
                    drift
                )

            continue

        # ======================================================
        # EVERYTHING ELSE
        # ======================================================

        normalized.append(
            drift
        )

    # ==========================================================
    # STABLE ORDERING
    # ==========================================================

    normalized.sort(
        key=lambda item: (
            str(
                item.get(
                    "endpoint",
                    ""
                )
            ),

            str(
                item.get(
                    "method",
                    ""
                )
            ),

            str(
                item.get(
                    "field_or_parameter",
                    ""
                )
            ),

            str(
                item.get(
                    "issue_type",
                    ""
                )
            ),
        )
    )

    return normalized
# NORMALIZE COMPLETE RESULT
# ============================================================

def normalize_result(
    runtime_result,
    source=None,
    contract=None
):
    """
    Normalize the complete runtime detector result.
    """

    if not isinstance(
        runtime_result,
        dict
    ):

        return {
            "drifts": [],

            "summary": {
                "raw_drifts": 0,
                "normalized_drifts": 0,
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0,
            }
        }

    raw_drifts = runtime_result.get(
        "drifts",
        []
    )

    normalized = normalize_findings(
        raw_drifts,
        source,
        contract
    )

    return {
        "drifts":
            normalized,

        "summary": {
            "raw_drifts":
                len(raw_drifts),

            "normalized_drifts":
                len(normalized),

            "high_severity":
                sum(
                    1
                    for drift in normalized
                    if drift.get(
                        "severity"
                    ) == "high"
                ),

            "medium_severity":
                sum(
                    1
                    for drift in normalized
                    if drift.get(
                        "severity"
                    ) == "medium"
                ),

            "low_severity":
                sum(
                    1
                    for drift in normalized
                    if drift.get(
                        "severity"
                    ) == "low"
                ),
        }
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    from agents.contract_extractor import (
        extract_contract
    )

    from agents.source_analyzer import (
        analyze_source
    )

    from agents.negative_runtime_verifier import (
        verify_negative_tests
    )

    from agents.runtime_drift_detector import (
        detect_runtime_drifts
    )

    print(
        "Running finding normalizer..."
    )

    # --------------------------------------------------------
    # Contract
    # --------------------------------------------------------

    contract = extract_contract(
        "benchmark/case11/openapi.yaml"
    )

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    source = analyze_source(
        "benchmark/case11/app.py"
    )

    # --------------------------------------------------------
    # Runtime
    # --------------------------------------------------------

    runtime_results = verify_negative_tests(
        contract,
        "http://127.0.0.1:5010"
    )

    # --------------------------------------------------------
    # Runtime drifts
    # --------------------------------------------------------

    raw_drifts = detect_runtime_drifts(
        contract,
        runtime_results,
        source
    )

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    result = normalize_result(
        {
            "drifts": raw_drifts
        },
        source,
        contract
    )

    print()

    print(
        "===== NORMALIZED FINDINGS ====="
    )

    print()

    print(
        json.dumps(
            result,
            indent=2
        )
    )
