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
# IMPORTS
# ============================================================

from agents.contract_extractor import extract_contract

from agents.negative_runtime_verifier import (
    verify_negative_tests
)

from agents.source_analyzer import (
    analyze_source
)


# ============================================================
# TYPE HELPERS
# ============================================================

def normalize_type(value):
    """
    Normalize common Python/OpenAPI type names.
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
    Infer the JSON/API type of a concrete value.
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
# CONTRACT LOOKUP
# ============================================================

def get_contract_endpoint(
    contract,
    endpoint_path,
    method
):
    """
    Find an endpoint in the extracted contract.
    """

    method = str(method).upper()

    for endpoint in contract.get(
        "endpoints",
        []
    ):

        if endpoint.get(
            "path"
        ) != endpoint_path:
            continue

        if endpoint.get(
            "method",
            ""
        ).upper() != method:
            continue

        return endpoint

    return None


def get_contract_property(
    contract,
    endpoint_path,
    method,
    field
):
    """
    Find a request-body property in the contract.
    """

    endpoint = get_contract_endpoint(
        contract,
        endpoint_path,
        method
    )

    if endpoint is None:
        return None

    request_body = endpoint.get(
        "request_body"
    )

    if not request_body:
        return None

    properties = request_body.get(
        "properties",
        {}
    )

    return properties.get(
        field
    )


# ============================================================
# SOURCE LOOKUP
# ============================================================

def get_source_route(
    source,
    endpoint,
    method
):
    """
    Find the corresponding source route.
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

        route_methods = [
            str(m).upper()
            for m in route.get(
                "methods",
                []
            )
        ]

        if method not in route_methods:
            continue

        if route.get(
            "normalized_path"
        ) == endpoint:
            return route

        if route.get(
            "path"
        ) == endpoint:
            return route

    return None


def get_source_request_field(
    source,
    endpoint,
    method,
    field
):
    """
    Get source information for a request-body field.
    """

    route = get_source_route(
        source,
        endpoint,
        method
    )

    if route is None:
        return None

    return route.get(
        "request_body_fields",
        {}
    ).get(
        field
    )


# ============================================================
# RUNTIME RESPONSE LOOKUP
# ============================================================

def get_runtime_response_field(
    result,
    field
):
    """
    Extract a field from the runtime response body.

    Returns:
        value

    If the response does not contain the field,
        returns None.
    """

    response_body = result.get(
        "response_body"
    )

    if not isinstance(
        response_body,
        dict
    ):
        return None

    return response_body.get(
        field
    )


# ============================================================
# DIRECT JSON DATA-FLOW CHECK
# ============================================================

def is_direct_json_field(
    source_field,
    field
):
    """
    Determine whether the source analyzer found the field
    flowing directly from request JSON.

    Example:

        data.get("quantity")

    This is useful evidence, but it does not itself establish
    the type.
    """

    if not isinstance(
        source_field,
        dict
    ):
        return False

    if source_field.get(
        "request_source"
    ) != "json_body":
        return False

    expression = source_field.get(
        "source_expression",
        ""
    )

    expected_expression = (
        f'data.get("{field}")'
    )

    if expression == expected_expression:
        return True

    # Allow equivalent request variable names.
    if (
        source_field.get(
            "access"
        ) == "get"
    ):
        return True

    return False


# ============================================================
# TYPE DRIFT
# ============================================================

def create_type_drift(
    result,
    property_schema,
    actual_type=None
):
    """
    Create a request-body type mismatch finding.
    """

    field = result.get(
        "field"
    )

    request_body = result.get(
        "request_body",
        {}
    )

    invalid_value = request_body.get(
        field
    )

    expected_type = normalize_type(
        property_schema.get(
            "type"
        )
    )

    if actual_type is None:
        actual_type = infer_value_type(
            invalid_value
        )

    return {
        "endpoint":
            result.get(
                "endpoint"
            ),

        "method":
            result.get(
                "method"
            ),

        "issue_type":
            "request_body_type_mismatch",

        "field_or_parameter":
            field,

        "expected":
            expected_type,

        "actual":
            actual_type,

        "severity":
            "medium",

        "evidence": {
            "test_type":
                result.get(
                    "test_type"
                ),

            "invalid_value":
                invalid_value,

            "invalid_value_type":
                infer_value_type(
                    invalid_value
                ),

            "runtime_value":
                get_runtime_response_field(
                    result,
                    field
                ),

            "runtime_value_type":
                actual_type,

            "status_code":
                result.get(
                    "status_code"
                ),

            "validation_enforced":
                result.get(
                    "validation_enforced"
                ),

            "response_body":
                result.get(
                    "response_body"
                ),
        },
    }


# ============================================================
# CONSTRAINT DRIFT
# ============================================================

def create_constraint_drift(
    result,
    property_schema
):
    """
    Create a constraint violation finding.
    """

    field = result.get(
        "field"
    )

    test_type = result.get(
        "test_type"
    )

    invalid_value = result.get(
        "request_body",
        {}
    ).get(
        field
    )

    expected = None
    issue_type = "constraint_mismatch"

    if test_type == "minimum_violation":

        minimum = property_schema.get(
            "minimum"
        )

        expected = f"minimum {minimum}"

    elif test_type == "maximum_violation":

        maximum = property_schema.get(
            "maximum"
        )

        expected = f"maximum {maximum}"

    elif test_type == "minLength_violation":

        minimum = property_schema.get(
            "minLength"
        )

        expected = f"minLength {minimum}"

    elif test_type == "maxLength_violation":

        maximum = property_schema.get(
            "maxLength"
        )

        expected = f"maxLength {maximum}"

    elif test_type == "minItems_violation":

        minimum = property_schema.get(
            "minItems"
        )

        expected = f"minItems {minimum}"

        issue_type = (
            "array_constraint_mismatch"
        )

    elif test_type == "maxItems_violation":

        maximum = property_schema.get(
            "maxItems"
        )

        expected = f"maxItems {maximum}"

        issue_type = (
            "array_constraint_mismatch"
        )

    elif test_type == "enum_violation":

        enum = property_schema.get(
            "enum"
        )

        expected = f"one of {enum}"

        issue_type = "enum_mismatch"

    else:
        return None

    actual = (
        f"{invalid_value} accepted"
    )

    return {
        "endpoint":
            result.get(
                "endpoint"
            ),

        "method":
            result.get(
                "method"
            ),

        "issue_type":
            issue_type,

        "field_or_parameter":
            field,

        "expected":
            expected,

        "actual":
            actual,

        "severity":
            "high",

        "evidence": {
            "test_type":
                test_type,

            "invalid_value":
                invalid_value,

            "status_code":
                result.get(
                    "status_code"
                ),

            "validation_enforced":
                result.get(
                    "validation_enforced"
                ),
        },
    }


# ============================================================
# NULLABILITY DRIFT
# ============================================================

def create_nullability_drift(
    result,
    property_schema
):
    """
    Create a nullability mismatch.
    """

    if property_schema.get(
        "nullable",
        False
    ):
        return None

    return {
        "endpoint":
            result.get(
                "endpoint"
            ),

        "method":
            result.get(
                "method"
            ),

        "issue_type":
            "nullability_mismatch",

        "field_or_parameter":
            result.get(
                "field"
            ),

        "expected":
            "non-null",

        "actual":
            "null accepted",

        "severity":
            "high",

        "evidence": {
            "test_type":
                result.get(
                    "test_type"
                ),

            "invalid_value":
                None,

            "status_code":
                result.get(
                    "status_code"
                ),

            "validation_enforced":
                result.get(
                    "validation_enforced"
                ),
        },
    }


# ============================================================
# TYPE TEST ANALYSIS
# ============================================================

def analyze_type_violation(
    result,
    property_schema,
    source
):
    """
    Analyze an accepted type-violation test.

    Strong evidence requires:

    1. The request value violates the documented type.
    2. The source receives that field directly from JSON.
    3. The endpoint accepts the request.
    4. The response contains the same field.
    5. The response preserves the invalid value/type.

    This avoids blindly reporting every accepted invalid
    request as a contract drift.
    """

    field = result.get(
        "field"
    )

    request_body = result.get(
        "request_body",
        {}
    )

    invalid_value = request_body.get(
        field
    )

    invalid_type = infer_value_type(
        invalid_value
    )

    expected_type = normalize_type(
        property_schema.get(
            "type"
        )
    )

    # The generated negative value must actually violate
    # the documented contract type.
    if (
        invalid_type == "unknown"
        or expected_type is None
    ):
        return None

    if invalid_type == expected_type:
        return None

    # --------------------------------------------------------
    # Source evidence
    # --------------------------------------------------------

    source_field = get_source_request_field(
        source,
        result.get("endpoint"),
        result.get("method"),
        field
    )

    if not is_direct_json_field(
        source_field,
        field
    ):
        return None

    # --------------------------------------------------------
    # Runtime must have accepted the invalid request.
    # --------------------------------------------------------

    if result.get(
        "validation_enforced"
    ):
        return None

    status_code = result.get(
        "status_code"
    )

    if status_code is None:
        return None

    # --------------------------------------------------------
    # Runtime response evidence
    # --------------------------------------------------------

    runtime_value = (
        get_runtime_response_field(
            result,
            field
        )
    )

    response_body = result.get(
        "response_body"
    )

    if not isinstance(
        response_body,
        dict
    ):
        return None

    if field not in response_body:
        return None

    runtime_type = infer_value_type(
        runtime_value
    )

    # We need the response to preserve the invalid type.
    #
    # Example:
    #
    # Contract: integer
    # Request:  "2"
    # Response: "2"
    #
    # This is strong evidence that the wrong type is flowing
    # through the implementation.
    if runtime_type != invalid_type:
        return None

    # The runtime value should preserve the request value.
    if runtime_value != invalid_value:
        return None

    return create_type_drift(
        result,
        property_schema,
        actual_type=runtime_type
    )


# ============================================================
# MAIN RUNTIME DRIFT DETECTOR
# ============================================================

def detect_runtime_drifts(
    contract,
    runtime_results,
    source=None
):
    """
    Convert runtime negative-test evidence into
    normalized drift candidates.
    """

    drifts = []

    if source is None:
        source = {}

    for result in runtime_results.get(
        "results",
        []
    ):

        # ----------------------------------------------------
        # Skip tests where validation worked.
        # ----------------------------------------------------

        if result.get(
            "validation_enforced"
        ):
            continue

        endpoint = result.get(
            "endpoint"
        )

        method = result.get(
            "method"
        )

        field = result.get(
            "field"
        )

        test_type = result.get(
            "test_type"
        )

        # ----------------------------------------------------
        # Contract property
        # ----------------------------------------------------

        property_schema = get_contract_property(
            contract,
            endpoint,
            method,
            field
        )

        if property_schema is None:
            continue

        # ====================================================
        # TYPE VIOLATION
        # ====================================================

        if test_type == "type_violation":

            drift = analyze_type_violation(
                result,
                property_schema,
                source
            )

            if drift:
                drifts.append(
                    drift
                )

            continue

        # ====================================================
        # CONSTRAINT VIOLATION
        # ====================================================

        if test_type in {
            "minimum_violation",
            "maximum_violation",
            "minLength_violation",
            "maxLength_violation",
            "minItems_violation",
            "maxItems_violation",
            "enum_violation",
        }:

            drift = create_constraint_drift(
                result,
                property_schema
            )

            if drift:
                drifts.append(
                    drift
                )

            continue
        # ====================================================
        # REQUIRED FIELD VIOLATION
        # ====================================================

               # ====================================================
        # REQUIRED FIELD VIOLATION
        # ====================================================

        if test_type == "required_field_violation":

            expected_status = 400

            actual_status = result.get(
                "status_code"
            )

            field_name = result.get(
                "field"
            )

            # The API accepted a request that omitted
            # a field documented as required.
            if (
                actual_status is not None
                and actual_status < 400
            ):

                drifts.append({
                    "endpoint":
                        result.get(
                            "endpoint"
                        ),

                    "method":
                        result.get(
                            "method"
                        ),

                    "issue_type":
                        "missing_required_request_field",

                    "field_or_parameter":
                        field_name,

                    "expected":
                        "required",

                    "actual":
                        "missing",

                    "severity":
                        "high",

                    "evidence": {
                        "test_type":
                            "required_field_violation",

                        "field":
                            field_name,

                        "expected_status":
                            expected_status,

                        "actual_status":
                            actual_status,

                        "validation_enforced":
                            False,
                    }
                })

            continue
        # ====================================================
        # NULLABILITY VIOLATION
        # ====================================================

        if test_type == "nullability_violation":

            drift = create_nullability_drift(
                result,
                property_schema
            )

            if drift:
                drifts.append(
                    drift
                )

            continue

    return drifts


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "Running runtime drift detector..."
    )

    contract = extract_contract(
        "benchmark/case11/openapi.yaml"
    )

    source = analyze_source(
        "benchmark/case11/app.py"
    )

    runtime_results = verify_negative_tests(
        contract,
        "http://127.0.0.1:5010"
    )

    drifts = detect_runtime_drifts(
        contract,
        runtime_results,
        source
    )

    result = {
        "drifts":
            drifts,

        "summary": {
            "total_drifts":
                len(drifts),

            "high_severity":
                sum(
                    1
                    for drift in drifts
                    if drift.get(
                        "severity"
                    ) == "high"
                ),

            "medium_severity":
                sum(
                    1
                    for drift in drifts
                    if drift.get(
                        "severity"
                    ) == "medium"
                ),

            "low_severity":
                sum(
                    1
                    for drift in drifts
                    if drift.get(
                        "severity"
                    ) == "low"
                ),
        },
    }

    print()

    print(
        json.dumps(
            result,
            indent=2
        )
    )