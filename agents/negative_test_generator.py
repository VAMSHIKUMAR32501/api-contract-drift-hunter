import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.contract_extractor import extract_contract


# ============================================================
# INVALID VALUE HELPERS
# ============================================================

def wrong_type_for(schema_type):
    """
    Return a value with a deliberately incorrect type.
    """

    if schema_type == "integer":
        return "2"

    if schema_type == "number":
        return "2"

    if schema_type == "string":
        return 123

    if schema_type == "boolean":
        return "true"

    if schema_type == "array":
        return "not-an-array"

    if schema_type == "object":
        return "not-an-object"

    return "invalid"


def below_minimum(schema):
    """
    Generate a value below the documented minimum.
    """

    minimum = schema.get("minimum")

    if minimum is None:
        return None

    return minimum - 1


def above_maximum(schema):
    """
    Generate a value above the documented maximum.
    """

    maximum = schema.get("maximum")

    if maximum is None:
        return None

    return maximum + 1


def too_short(schema):
    """
    Generate a string shorter than minLength.
    """

    minimum = schema.get("minLength")

    if minimum is None:
        return None

    if minimum <= 0:
        return None

    return "a" * (minimum - 1)


def too_long(schema):
    """
    Generate a string longer than maxLength.
    """

    maximum = schema.get("maxLength")

    if maximum is None:
        return None

    return "a" * (maximum + 1)


def too_few_items(schema):
    """
    Generate an array with fewer items than minItems.
    """

    minimum = schema.get("minItems")

    if minimum is None:
        return None

    if minimum <= 0:
        return None

    return []


def too_many_items(schema):
    """
    Generate an array with more items than maxItems.
    """

    maximum = schema.get("maxItems")

    if maximum is None:
        return None

    return [
        None
        for _ in range(maximum + 1)
    ]


def invalid_enum_value(schema):
    """
    Generate a value that is not present in the enum.
    """

    enum = schema.get("enum")

    if not enum:
        return None

    schema_type = schema.get(
        "type"
    )

    candidate = "INVALID_ENUM_VALUE"

    if schema_type == "integer":
        candidate = 999999

    elif schema_type == "number":
        candidate = 999999.99

    elif schema_type == "boolean":
        candidate = None

    if candidate in enum:
        candidate = "__invalid__"

    if candidate in enum:
        return None

    return candidate


def nullable_violation(schema):
    """
    Generate null for a non-nullable field.

    Kept for compatibility with the existing
    negative-test generation behavior.
    """

    nullable = schema.get(
        "nullable",
        False
    )

    if nullable:
        return None

    return None


# ============================================================
# PROPERTY TEST GENERATION
# ============================================================

def generate_property_tests(
    name,
    schema
):
    """
    Generate targeted negative tests for
    one request-body property.
    """

    tests = []

    schema_type = schema.get(
        "type"
    )

    # ------------------------------------------
    # Wrong type
    # ------------------------------------------

    wrong_type = wrong_type_for(
        schema_type
    )

    tests.append({
        "field": name,
        "test_type": "type_violation",
        "expected_type": schema_type,
        "invalid_value": wrong_type,
    })

    # ------------------------------------------
    # Minimum
    # ------------------------------------------

    invalid_value = below_minimum(
        schema
    )

    if invalid_value is not None:

        tests.append({
            "field": name,
            "test_type":
                "minimum_violation",
            "expected_minimum":
                schema.get(
                    "minimum"
                ),
            "invalid_value":
                invalid_value,
        })

    # ------------------------------------------
    # Maximum
    # ------------------------------------------

    invalid_value = above_maximum(
        schema
    )

    if invalid_value is not None:

        tests.append({
            "field": name,
            "test_type":
                "maximum_violation",
            "expected_maximum":
                schema.get(
                    "maximum"
                ),
            "invalid_value":
                invalid_value,
        })

    # ------------------------------------------
    # minLength
    # ------------------------------------------

    invalid_value = too_short(
        schema
    )

    if invalid_value is not None:

        tests.append({
            "field": name,
            "test_type":
                "minLength_violation",
            "expected_minLength":
                schema.get(
                    "minLength"
                ),
            "invalid_value":
                invalid_value,
        })

    # ------------------------------------------
    # maxLength
    # ------------------------------------------

    invalid_value = too_long(
        schema
    )

    if invalid_value is not None:

        tests.append({
            "field": name,
            "test_type":
                "maxLength_violation",
            "expected_maxLength":
                schema.get(
                    "maxLength"
                ),
            "invalid_value":
                invalid_value,
        })

    # ------------------------------------------
    # minItems
    # ------------------------------------------

    invalid_value = too_few_items(
        schema
    )

    if invalid_value is not None:

        tests.append({
            "field": name,
            "test_type":
                "minItems_violation",
            "expected_minItems":
                schema.get(
                    "minItems"
                ),
            "invalid_value":
                invalid_value,
        })

    # ------------------------------------------
    # maxItems
    # ------------------------------------------

    invalid_value = too_many_items(
        schema
    )

    if invalid_value is not None:

        tests.append({
            "field": name,
            "test_type":
                "maxItems_violation",
            "expected_maxItems":
                schema.get(
                    "maxItems"
                ),
            "invalid_value":
                invalid_value,
        })

    # ------------------------------------------
    # Enum
    # ------------------------------------------

    invalid_value = invalid_enum_value(
        schema
    )

    if invalid_value is not None:

        tests.append({
            "field": name,
            "test_type":
                "enum_violation",
            "expected_enum":
                schema.get(
                    "enum"
                ),
            "invalid_value":
                invalid_value,
        })

    # ------------------------------------------
    # Nullability
    # ------------------------------------------

    if (
        not schema.get(
            "required",
            False
        )
        and not schema.get(
            "nullable",
            False
        )
    ):

        tests.append({
            "field": name,
            "test_type":
                "nullability_violation",
            "expected_nullable":
                False,
            "invalid_value":
                None,
        })

    return tests


# ============================================================
# SHOULD GENERATE PROPERTY TESTS?
# ============================================================

def has_explicit_constraint(schema):
    """
    Determine whether a property has an explicit
    schema constraint beyond its basic type.

    This is important for endpoints that contain
    required fields.

    Example:

        case06:
            email -> string
            name  -> string

        There are no explicit property constraints,
        so generating type violations would create
        noisy false positives.

        case11:
            quantity -> integer
            minimum -> 1

        The explicit minimum tells us that this
        property has meaningful negative-test
        behavior, so property tests are generated.
    """

    constraint_keys = {
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "minLength",
        "maxLength",
        "pattern",
        "minItems",
        "maxItems",
        "uniqueItems",
        "enum",
        "format",
        "nullable",
        "oneOf",
        "anyOf",
        "allOf",
    }

    return any(
        key in schema
        for key in constraint_keys
    )


def should_generate_property_tests(
    properties,
    required_fields
):
    """
    Decide which properties should receive
    property-level negative tests.

    Rules:

    1. No required fields:
       test every property.

    2. Required fields exist:
       only test properties with explicit
       schema constraints.

    This avoids case06-style false positives
    while allowing constrained fields such as
    case11.quantity to be tested.
    """

    selected = []

    if not required_fields:

        return list(
            properties.items()
        )

    for name, schema in properties.items():

        if has_explicit_constraint(
            schema
        ):
            selected.append(
                (name, schema)
            )

    return selected


# ============================================================
# BUILD VALID BODY
# ============================================================

def build_valid_body(
    properties,
    excluded_field=None
):
    """
    Build a simple valid-ish request body.

    The excluded field is omitted when creating
    a required-field violation.
    """

    body = {}

    for field_name, field_schema in (
        properties.items()
    ):

        if field_name == excluded_field:
            continue

        field_type = field_schema.get(
            "type"
        )

        if field_type == "integer":
            body[field_name] = 1

        elif field_type == "number":
            body[field_name] = 1.0

        elif field_type == "string":
            body[field_name] = "test"

        elif field_type == "boolean":
            body[field_name] = True

        elif field_type == "array":
            body[field_name] = []

        elif field_type == "object":
            body[field_name] = {}

        else:
            body[field_name] = None

    return body


# ============================================================
# BUILD PROPERTY VIOLATION BODY
# ============================================================

def build_property_violation_body(
    properties,
    target_field,
    invalid_value
):
    """
    Build a request body containing one
    deliberately invalid property value.
    """

    body = {}

    for field_name, field_schema in (
        properties.items()
    ):

        field_type = field_schema.get(
            "type"
        )

        if field_name == target_field:

            body[field_name] = (
                invalid_value
            )

        elif field_type == "integer":

            body[field_name] = 1

        elif field_type == "number":

            body[field_name] = 1.0

        elif field_type == "string":

            body[field_name] = "test"

        elif field_type == "boolean":

            body[field_name] = True

        elif field_type == "array":

            body[field_name] = []

        elif field_type == "object":

            body[field_name] = {}

        else:

            body[field_name] = None

    return body


# ============================================================
# NEGATIVE TEST GENERATION FOR ONE ENDPOINT
# ============================================================

def generate_negative_tests(endpoint):
    """
    Generate targeted negative tests for an endpoint.

    Includes:

    - type violations
    - numeric/string constraints
    - enum violations
    - nullability violations
    - missing required request-body fields
    """

    tests = []

    request_body = endpoint.get(
        "request_body"
    )

    if not request_body:
        return tests

    properties = request_body.get(
        "properties",
        {}
    )

    if not isinstance(
        properties,
        dict
    ):
        return tests

    required_fields = {
        name
        for name, schema in properties.items()
        if isinstance(schema, dict)
        and schema.get(
            "required",
            False
        )
    }

    # =========================================================
    # REQUIRED FIELD VIOLATIONS
    # =========================================================

    # Preserve existing behavior:
    # generate only one required-field test
    # for an endpoint.

    for required_field in sorted(
        required_fields
    )[:1]:

        if required_field not in properties:
            continue

        body = build_valid_body(
            properties,
            excluded_field=required_field
        )

        tests.append({
            "method":
                endpoint.get(
                    "method",
                    "GET"
                ),

            "path":
                endpoint.get(
                    "path",
                    ""
                ),

            "test_type":
                "required_field_violation",

            "field":
                required_field,

            "body":
                body,

            "expected_contract_type":
                properties[
                    required_field
                ].get(
                    "type"
                ),

            "invalid_value":
                None,
        })

    # =========================================================
    # PROPERTY-LEVEL VIOLATIONS
    # =========================================================

    selected_properties = (
        should_generate_property_tests(
            properties,
            required_fields
        )
    )

    for name, schema in (
        selected_properties
    ):

        property_tests = (
            generate_property_tests(
                name,
                schema
            )
        )

        for test in property_tests:

            body = (
                build_property_violation_body(
                    properties,
                    name,
                    test.get(
                        "invalid_value"
                    )
                )
            )

            tests.append({
                "method":
                    endpoint.get(
                        "method",
                        "GET"
                    ),

                "path":
                    endpoint.get(
                        "path",
                        ""
                    ),

                "test_type":
                    test.get(
                        "test_type"
                    ),

                "field":
                    name,

                "body":
                    body,

                "expected_contract_type":
                    test.get(
                        "expected_type"
                    ),

                "invalid_value":
                    test.get(
                        "invalid_value"
                    ),
            })

    return tests


# ============================================================
# NEGATIVE TEST GENERATION FOR COMPLETE CONTRACT
# ============================================================

def generate_negative_tests_for_contract(
    contract,
    source=None
):
    """
    Generate negative tests for every endpoint
    in the extracted contract.
    """

    all_tests = []

    if not isinstance(
        contract,
        dict
    ):
        return all_tests

    endpoints = contract.get(
        "endpoints",
        []
    )

    if not isinstance(
        endpoints,
        list
    ):
        return all_tests

    for endpoint in endpoints:

        if not isinstance(
            endpoint,
            dict
        ):
            continue

        endpoint_tests = (
            generate_negative_tests(
                endpoint
            )
        )

        all_tests.extend(
            endpoint_tests
        )

    return all_tests


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "Generating negative tests for Case 11..."
    )

    contract = extract_contract(
        "benchmark/case11/openapi.yaml"
    )

    tests = (
        generate_negative_tests_for_contract(
            contract
        )
    )

    print()

    print(
        json.dumps(
            tests,
            indent=2
        )
    )