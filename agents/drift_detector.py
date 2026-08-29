import json
import sys
from pathlib import Path


# Allow imports when running this file directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.contract_extractor import extract_contract
from agents.source_analyzer import analyze_source


def find_matching_source_route(
    contract_endpoint,
    source_routes
):
    """
    Find the source route corresponding to an
    OpenAPI endpoint.

    Both sides use normalized paths.

    Example:

        /users/{id}
        /users/<int:user_id>

    become:

        /users/{param}
    """

    normalized_path = contract_endpoint[
        "normalized_path"
    ]

    method = contract_endpoint[
        "method"
    ]

    for route in source_routes:

        if (
            route["normalized_path"]
            == normalized_path
            and method in route["methods"]
        ):
            return route

    return None

def get_success_response_branches(
    contract_endpoint,
    source_route,
    status_code
):
    """
    Return source response branches corresponding to a
    documented successful response.

    When multiple branches use the same status code, prefer
    the branch that contains fields documented by the contract.

    This prevents an unconditional error/fallback response
    from being mistaken for the successful response.
    """

    response_fields_by_status = (
        source_route.get(
            "response_fields_by_status",
            {}
        )
    )

    branches = (
        response_fields_by_status.get(
            str(status_code),
            []
        )
    )

    if isinstance(
        branches,
        dict
    ):
        branches = [
            branches
        ]

    if not isinstance(
        branches,
        list
    ):
        return []

    # --------------------------------------------------------
    # For successful responses, prefer the branch containing
    # documented response fields.
    # --------------------------------------------------------

    if status_code < 400:

        contract_response = (
            contract_endpoint
            .get("responses", {})
            .get(str(status_code), {})
        )

        contract_properties = (
            contract_response.get(
                "properties",
                {}
            )
        )

        if contract_properties:

            matching_branches = []

            for branch in branches:

                if not isinstance(
                    branch,
                    dict
                ):
                    continue

                overlap = (
                    set(branch.keys())
                    &
                    set(contract_properties.keys())
                )

                if overlap:
                    matching_branches.append(
                        branch
                    )

            if matching_branches:
                return matching_branches

    return branches
def detect_response_type_drifts(
    contract_endpoint,
    source_route
):
    """
    Compare documented successful-response field types
    against the corresponding source response branches.
    """

    drifts = []

    responses = contract_endpoint.get(
        "responses",
        {}
    )

    for status_code, response in responses.items():

        if not str(status_code).startswith("2"):
            continue

        try:
            status = int(status_code)
        except (
            TypeError,
            ValueError
        ):
            continue

        contract_properties = response.get(
            "properties",
            {}
        )

        if not contract_properties:
            continue

        source_branches = (
            get_success_response_branches(
                contract_endpoint,
                source_route,
                status
            )
        )

        for source_properties in source_branches:

            if not isinstance(
                source_properties,
                dict
            ):
                continue

            for field_name, contract_field in (
                contract_properties.items()
            ):

                source_field = (
                    source_properties.get(
                        field_name
                    )
                )

                if not isinstance(
                    source_field,
                    dict
                ):
                    continue

                expected_type = (
                    contract_field.get(
                        "type"
                    )
                )

                actual_type = (
                    source_field.get(
                        "type"
                    )
                )

                if (
                    expected_type
                    and actual_type
                    and actual_type != "unknown"
                    and expected_type != actual_type
                ):

                    drifts.append({
                        "endpoint":
                            contract_endpoint["path"],

                        "method":
                            contract_endpoint["method"],

                        "issue_type":
                            "response_type_mismatch",

                        "field_or_parameter":
                            field_name,

                        "expected":
                            expected_type,

                        "actual":
                            actual_type,

                        "evidence": {
                            "source_value":
                                source_field.get(
                                    "value"
                                ),

                            "documented_type":
                                expected_type,

                            "observed_type":
                                actual_type,

                            "source_expression":
                                source_field.get(
                                    "source_expression"
                                ),
                        }
                    })

    return drifts


def detect_missing_response_fields(
    contract_endpoint,
    source_route
):
    """
    Detect required fields missing from documented
    successful response branches.

    Only the source branch corresponding to the documented
    successful status is inspected.
    """

    drifts = []

    responses = contract_endpoint.get(
        "responses",
        {}
    )

    for status_code, response in responses.items():

        if not str(status_code).startswith("2"):
            continue

        try:
            status = int(status_code)
        except (
            TypeError,
            ValueError
        ):
            continue

        contract_properties = response.get(
            "properties",
            {}
        )

        if not contract_properties:
            continue

        source_branches = (
            get_success_response_branches(
                contract_endpoint,
                source_route,
                status
            )
        )

        if not source_branches:
            continue

        for source_properties in source_branches:

            if not isinstance(
                source_properties,
                dict
            ):
                continue

            for field_name, contract_field in (
                contract_properties.items()
            ):

                if not contract_field.get(
                    "required",
                    False
                ):
                    continue

                if field_name not in source_properties:

                    drifts.append({
                        "endpoint":
                            contract_endpoint["path"],

                        "method":
                            contract_endpoint["method"],

                        "issue_type":
                            "missing_required_response_field",

                        "field_or_parameter":
                            field_name,

                        "expected":
                            "required",

                        "actual":
                            "missing",

                        "evidence": {
                            "documented_required":
                                True,

                            "source_field_present":
                                False,

                            "status_code":
                                status,
                        }
                    })

    return drifts
def detect_extra_response_fields(
    contract_endpoint,
    source_route
):
    """
    Detect fields returned by a successful source response
    that are not documented for that successful response.
    """

    drifts = []

    responses = contract_endpoint.get(
        "responses",
        {}
    )

    for status_code, response in responses.items():

        if not str(status_code).startswith("2"):
            continue

        try:
            status = int(status_code)
        except (
            TypeError,
            ValueError
        ):
            continue

        contract_properties = response.get(
            "properties",
            {}
        )

        if not contract_properties:
            continue

        source_branches = (
            get_success_response_branches(
                contract_endpoint,
                source_route,
                status
            )
        )

        for source_properties in source_branches:

            if not isinstance(
                source_properties,
                dict
            ):
                continue

            for field_name in source_properties:

                if field_name not in contract_properties:

                    drifts.append({
                        "endpoint":
                            contract_endpoint["path"],

                        "method":
                            contract_endpoint["method"],

                        "issue_type":
                            "undocumented_response_field",

                        "field_or_parameter":
                            field_name,

                        "expected":
                            "not documented",

                        "actual":
                            "returned",

                        "evidence": {
                            "documented":
                                False,

                            "source_field_present":
                                True,

                            "status_code":
                                status,
                        }
                    })

    return drifts
def detect_error_response_schema_drifts(
    contract_endpoint,
    source_route
):
    """
    Detect mismatches between documented error-response
    fields and fields actually returned by the implementation.

    Produces one finding for the entire error-response schema.
    """

    drifts = []

    responses = contract_endpoint.get(
        "responses",
        {}
    )

    response_fields_by_status = (
        source_route.get(
            "response_fields_by_status",
            {}
        )
    )

    source_statuses = source_route.get(
        "response_statuses",
        []
    )

    for status_code, response in responses.items():

        try:
            status = int(status_code)
        except (
            TypeError,
            ValueError
        ):
            continue

        # Only error responses.
        if status < 400:
            continue

        contract_properties = response.get(
            "properties",
            {}
        )

        if not contract_properties:
            continue

        # Confirm implementation actually returns this status.
        matching_source = None

        for item in source_statuses:

            if (
                isinstance(item, dict)
                and item.get("status_code") == status
            ):
                matching_source = item
                break

        if matching_source is None:
            continue
        source_properties = (
            response_fields_by_status.get(
                str(status),
                {}
            )
        )

        if not source_properties:
            continue

        expected_fields = set(
            contract_properties.keys()
        )

        # ----------------------------------------------------
        # response_fields_by_status can be either:
        #
        # 1. A single dictionary
        # 2. A list of response branches
        #
        # Example:
        #
        # "400": {
        #     "error": {...},
        #     "code": {...}
        # }
        #
        # OR:
        #
        # "200": [
        #     {"id": {...}, "name": {...}},
        #     {"error": {...}}
        # ]
        # ----------------------------------------------------

        if isinstance(
            source_properties,
            dict
        ):

            actual_fields = set(
                source_properties.keys()
            )

        elif isinstance(
            source_properties,
            list
        ):

            actual_fields = set()

            for branch in source_properties:

                if not isinstance(
                    branch,
                    dict
                ):
                    continue

                actual_fields.update(
                    branch.keys()
                )

        else:

            continue

        # ----------------------------------------------------
        # Compare documented fields with implementation fields.
        # ----------------------------------------------------

        missing_fields = (
            expected_fields
            - actual_fields
        )

        unexpected_fields = (
            actual_fields
            - expected_fields
        )

        if (
            not missing_fields
            and not unexpected_fields
        ):
            continue

        # ----------------------------------------------------
        # Required fields documented by the contract.
        # ----------------------------------------------------

        required_fields = [
            name
            for name, field in (
                contract_properties.items()
            )
            if isinstance(
                field,
                dict
            )
            and field.get(
                "required",
                False
            )
        ]

        drifts.append({
            "endpoint":
                contract_endpoint["path"],

            "method":
                contract_endpoint["method"],

            "issue_type":
                "error_response_schema_mismatch",

            "field_or_parameter":
                None,

            "expected": {
                "required_fields":
                    required_fields,

                "fields":
                    sorted(
                        expected_fields
                    ),
            },

            "actual": {
                "fields":
                    sorted(
                        actual_fields
                    ),
            },

            "severity":
                "high",

            "evidence": {
                "status_code":
                    status,

                "missing_fields":
                    sorted(
                        missing_fields
                    ),

                "unexpected_fields":
                    sorted(
                        unexpected_fields
                    ),

                "source_condition":
                    matching_source.get(
                        "condition"
                    ),
            }
        })
    return drifts
def detect_error_response_schema_drifts(
    contract_endpoint,
    source_route
):
    """
    Detect mismatches in documented error response schemas.

    Example:

        Contract 400:
            {
                "error": string,
                "code": string
            }

        Implementation 400:
            {
                "message": "Amount is required"
            }

    Produces one canonical finding instead of separate
    findings for every missing/unexpected field.
    """

    drifts = []

    responses = contract_endpoint.get(
        "responses",
        {}
    )

    source_statuses = source_route.get(
        "response_statuses",
        []
    )

    source_properties = source_route.get(
        "response_fields",
        {}
    )

    # Find documented error responses.
    for status_code, response in responses.items():

        try:
            status = int(status_code)
        except (
            TypeError,
            ValueError
        ):
            continue

        if status < 400:
            continue

        contract_properties = response.get(
            "properties",
            {}
        )

        required_fields = [
            name
            for name, field in contract_properties.items()
            if field.get("required", False)
        ]

        if not required_fields:
            continue

        # Find the source branch returning this status.
        matching_source = None

        for item in source_statuses:

            if (
                isinstance(item, dict)
                and item.get("status_code") == status
            ):
                matching_source = item
                break

        if matching_source is None:
            continue

        # IMPORTANT:
        # Only make this comparison when the source analyzer
        # actually knows the response fields.
        if not source_properties:
            continue

        # ----------------------------------------------------
        # response_fields_by_status can be either:
        # 1. a dictionary of fields
        # 2. a list of response branches
        # ----------------------------------------------------

        if isinstance(
            source_properties,
            dict
        ):

            actual_fields = set(
                source_properties.keys()
            )

        elif isinstance(
            source_properties,
            list
        ):

            actual_fields = set()

            for branch in source_properties:

                if not isinstance(
                    branch,
                    dict
                ):
                    continue

                actual_fields.update(
                    branch.keys()
                )

        else:

            continue

        expected_fields = set(
            contract_properties.keys()
        )

        missing_fields = (
            expected_fields
            - actual_fields
        )

        unexpected_fields = (
            actual_fields
            - expected_fields
        )

        if not missing_fields and not unexpected_fields:
            continue

        drifts.append({
            "endpoint":
                contract_endpoint["path"],

            "method":
                contract_endpoint["method"],

            "issue_type":
                "error_response_schema_mismatch",

            "field_or_parameter":
                None,

            "expected": {
                "required_fields":
                    required_fields
            },

            "actual": {
                "fields":
                    sorted(actual_fields)
            },

            "severity":
                "high",

            "evidence": {
                "status_code":
                    status,

                "missing_fields":
                    sorted(missing_fields),

                "unexpected_fields":
                    sorted(unexpected_fields),

                "source_condition":
                    matching_source.get(
                        "condition"
                    ),
            }
        })

    return drifts

def detect_parameter_type_drifts(
    contract_endpoint,
    source_route
):
    """
    Compare OpenAPI path parameter types
    against Flask route converter types.
    """

    drifts = []

    contract_parameters = {
        parameter["name"]:
            parameter
        for parameter
        in contract_endpoint.get(
            "parameters",
            []
        )
    }

    source_parameters = source_route.get(
        "parameters",
        {}
    )

    for name, contract_parameter in (
        contract_parameters.items()
    ):

        expected_type = contract_parameter.get(
            "type"
        )

        # The Flask variable may have a different
        # name from the OpenAPI parameter.
        #
        # For example:
        #
        # OpenAPI: id
        # Flask:   user_id
        #
        # Match by position/name when possible.
        source_parameter = source_parameters.get(
            name
        )

        if source_parameter is None:

            # If there is only one source parameter
            # and one contract parameter, use it.
            if (
                len(source_parameters) == 1
                and len(contract_parameters) == 1
            ):
                source_parameter = next(
                    iter(
                        source_parameters.values()
                    )
                )

        if source_parameter is None:
            continue

        actual_type = source_parameter.get(
            "type"
        )

        if (
            expected_type
            and actual_type
            and actual_type != "unknown"
            and expected_type != actual_type
        ):

            drifts.append({
                "endpoint":
                    contract_endpoint["path"],

                "method":
                    contract_endpoint["method"],

                "issue_type":
                    "request_parameter_type_mismatch",

                "field_or_parameter":
                    name,

                "expected":
                    expected_type,

                "actual":
                    actual_type,

                "evidence": {
                    "documented_type":
                        expected_type,

                    "source_route_type":
                        actual_type,
                }
            })

    return drifts

def detect_response_status_drifts(
    contract_endpoint,
    source_route
):
    """
    Detect response status-code drift.

    A documented error status is considered a drift only when
    the implementation contains conditional response behavior
    indicating that a different response should occur under
    some condition.

    A normal unconditional success response is not considered
    a drift merely because the OpenAPI document also lists
    possible error responses.
    """

    drifts = []

    responses = contract_endpoint.get(
        "responses",
        {}
    )

    source_statuses = source_route.get(
        "response_statuses",
        []
    )

    if not source_statuses:
        return drifts

    # --------------------------------------------------------
    # Documented status codes
    # --------------------------------------------------------

    documented_statuses = set()

    for status_code in responses:

        try:
            documented_statuses.add(
                int(status_code)
            )
        except (
            TypeError,
            ValueError
        ):
            continue

    # --------------------------------------------------------
    # Actual source statuses
    # --------------------------------------------------------

    actual_statuses = {
        item.get("status_code")
        for item in source_statuses
        if isinstance(item, dict)
        and isinstance(
            item.get("status_code"),
            int
        )
    }

    # --------------------------------------------------------
    # Only investigate documented error statuses.
    # --------------------------------------------------------

    documented_error_statuses = {
        status
        for status in documented_statuses
        if status >= 400
    }

    if not documented_error_statuses:
        return drifts

    missing_error_statuses = (
        documented_error_statuses
        - actual_statuses
    )

    if not missing_error_statuses:
        return drifts

    # --------------------------------------------------------
    # We only infer a missing error response when the source
    # contains conditional response behavior.
    #
    # Case 11:
    #
    #     return jsonify(item), 201
    #
    # There is no conditional branch, so do NOT claim that
    # 400 is missing.
    # --------------------------------------------------------

    conditional_responses = [
        item
        for item in source_statuses
        if (
            isinstance(item, dict)
            and item.get("condition") is not None
            and isinstance(
                item.get("status_code"),
                int
            )
        )
    ]

    if not conditional_responses:
        return drifts

    # --------------------------------------------------------
    # Look for an unconditional fallback response.
    # --------------------------------------------------------

    fallback_responses = [
        item
        for item in source_statuses
        if (
            isinstance(item, dict)
            and item.get("condition") is None
            and isinstance(
                item.get("status_code"),
                int
            )
        )
    ]

    if not fallback_responses:
        return drifts

    fallback = fallback_responses[-1]

    actual_status = fallback.get(
        "status_code"
    )

    if actual_status >= 400:
        return drifts

    # --------------------------------------------------------
    # Prefer 404 for missing-resource conditions.
    # Otherwise use the first documented error status.
    # --------------------------------------------------------

    if 404 in missing_error_statuses:

        expected_status = 404

    else:

        expected_status = sorted(
            missing_error_statuses
        )[0]

    drifts.append({
        "endpoint":
            contract_endpoint["path"],

        "method":
            contract_endpoint["method"],

        "issue_type":
            "response_status_mismatch",

        "field_or_parameter":
            None,

        "expected":
            str(expected_status),

        "actual":
            str(actual_status),

        "severity":
            "high",

        "evidence": {
            "documented_status":
                expected_status,

            "implementation_status":
                actual_status,

            "source_condition":
                fallback.get(
                    "condition"
                ),

            "documented_error_statuses":
                sorted(
                    documented_error_statuses
                ),

            "actual_statuses":
                sorted(
                    actual_statuses
                ),
        }
    })

    return drifts
def detect_query_parameter_type_drifts(
    contract_endpoint,
    source_route
):
    """
    Compare OpenAPI query parameter types against
    Flask request.args usage.
    """

    drifts = []

    contract_parameters = contract_endpoint.get(
        "parameters",
        []
    )

    source_parameters = source_route.get(
        "query_parameters",
        {}
    )

    for parameter in contract_parameters:

        if parameter.get(
            "in"
        ) != "query":
            continue

        name = parameter.get(
            "name"
        )

        if name not in source_parameters:
            continue

        expected_type = parameter.get(
            "type"
        )

        source_parameter = (
            source_parameters[name]
        )

        actual_type = source_parameter.get(
            "type"
        )

        if (
            expected_type
            and actual_type
            and actual_type != "unknown"
            and expected_type != actual_type
        ):

            drifts.append({
                "endpoint":
                    contract_endpoint["path"],

                "method":
                    contract_endpoint["method"],

                "issue_type":
                    "request_parameter_type_mismatch",

                "field_or_parameter":
                    name,

                "expected":
                    expected_type,

                "actual":
                    actual_type,

                "severity":
                    "medium",

                "evidence": {
                    "documented_type":
                        expected_type,

                    "source_parameter_type":
                        actual_type,

                    "source_expression":
                        source_parameter.get(
                            "source_expression"
                        ),

                    "conversion":
                        source_parameter.get(
                            "conversion"
                        ),
                }
            })

    return drifts
def detect_response_enum_drifts(
    contract_endpoint,
    source_route
):
    """
    Detect response fields whose statically observed
    value is outside the enum documented by OpenAPI.

    Uses status-specific response branches so that
    different response paths are analyzed independently.
    """

    drifts = []

    responses = contract_endpoint.get(
        "responses",
        {}
    )

    response_fields_by_status = (
        source_route.get(
            "response_fields_by_status",
            {}
        )
    )

    # --------------------------------------------------------
    # Inspect each documented response.
    # --------------------------------------------------------

    for status_code, response in responses.items():

        # Enum checking is currently limited to
        # successful 2xx responses.
        if not str(status_code).startswith("2"):
            continue

        contract_properties = response.get(
            "properties",
            {}
        )

        if not contract_properties:
            continue

        # ----------------------------------------------------
        # Get source response branches for this status.
        #
        # Usually:
        #
        # {
        #     "200": [
        #         {...},
        #         {...}
        #     ]
        # }
        #
        # Also support a single dictionary for compatibility.
        # ----------------------------------------------------

        source_branches = (
            response_fields_by_status.get(
                str(status_code),
                []
            )
        )

        if isinstance(
            source_branches,
            dict
        ):
            source_branches = [
                source_branches
            ]

        if not isinstance(
            source_branches,
            list
        ):
            continue

        # ----------------------------------------------------
        # Inspect every source branch.
        # ----------------------------------------------------

        for source_properties in source_branches:

            if not isinstance(
                source_properties,
                dict
            ):
                continue

            # ------------------------------------------------
            # Compare every documented enum field.
            # ------------------------------------------------

            for field_name, contract_field in (
                contract_properties.items()
            ):

                allowed_values = (
                    contract_field.get(
                        "enum"
                    )
                )

                if not allowed_values:
                    continue

                source_field = (
                    source_properties.get(
                        field_name
                    )
                )

                if not isinstance(
                    source_field,
                    dict
                ):
                    continue

                actual_value = (
                    source_field.get(
                        "value"
                    )
                )

                # We need a concrete statically
                # observed value.
                if actual_value is None:
                    continue

                # ------------------------------------------------
                # ENUM VIOLATION
                # ------------------------------------------------

                if actual_value not in allowed_values:

                    drifts.append({
                        "endpoint":
                            contract_endpoint["path"],

                        "method":
                            contract_endpoint["method"],

                        "issue_type":
                            "response_enum_violation",

                        "field_or_parameter":
                            field_name,

                        "expected":
                            allowed_values,

                        "actual":
                            actual_value,

                        "severity":
                            "medium",

                        "evidence": {
                            "documented_enum":
                                allowed_values,

                            "source_value":
                                actual_value,

                            "source_expression":
                                source_field.get(
                                    "source_expression"
                                ),
                        }
                    })

    return drifts
def detect_error_response_schema_drifts(
    contract_endpoint,
    source_route
):
    """
    Detect mismatches in documented error response schemas.

    Produces one finding for the entire error response.
    """

    drifts = []

    responses = contract_endpoint.get(
        "responses",
        {}
    )

    response_fields_by_status = (
        source_route.get(
            "response_fields_by_status",
            {}
        )
    )

    source_statuses = source_route.get(
        "response_statuses",
        []
    )

    for status_code, response in responses.items():

        try:
            status = int(status_code)
        except (
            TypeError,
            ValueError
        ):
            continue

        # Only error responses.
        if status < 400:
            continue

        contract_properties = response.get(
            "properties",
            {}
        )

        if not contract_properties:
            continue

        # Confirm this status is actually returned.
        matching_source = None

        for item in source_statuses:

            if (
                isinstance(item, dict)
                and item.get("status_code") == status
            ):
                matching_source = item
                break

        if matching_source is None:
            continue

        source_properties = (
            response_fields_by_status.get(
                str(status),
                {}
            )
        )

        if not source_properties:
            continue

        expected_fields = set(
            contract_properties.keys()
        )

        if isinstance(source_properties, dict):
            actual_fields = set(
                source_properties.keys()
            )

        elif isinstance(source_properties, list):
            actual_fields = set()

            for branch in source_properties:
                if not isinstance(branch, dict):
                    continue
                actual_fields.update(
                    branch.keys()
                )

        else:
            continue
            continue

        expected_fields = set(
            contract_properties.keys()
        )


        missing_fields = (
            expected_fields
            - actual_fields
        )

        unexpected_fields = (
            actual_fields
            - expected_fields
        )

        if (
            not missing_fields
            and not unexpected_fields
        ):
            continue

        required_fields = [
            name
            for name, field in (
                contract_properties.items()
            )
            if field.get(
                "required",
                False
            )
        ]

        drifts.append({
            "endpoint":
                contract_endpoint["path"],

            "method":
                contract_endpoint["method"],

            "issue_type":
                "error_response_schema_mismatch",

            "field_or_parameter":
                None,

            "expected": {
                "required_fields":
                    required_fields,

                "fields":
                    sorted(
                        expected_fields
                    ),
            },

            "actual": {
                "fields":
                    sorted(
                        actual_fields
                    ),
            },

            "severity":
                "high",

            "evidence": {
                "status_code":
                    status,

                "missing_fields":
                    sorted(
                        missing_fields
                    ),

                "unexpected_fields":
                    sorted(
                        unexpected_fields
                    ),

                "source_condition":
                    matching_source.get(
                        "condition"
                    ),
            }
        })

    return drifts
def detect_drifts(
    openapi_path,
    source_path
):
    contract = extract_contract(
        openapi_path
    )

    source = analyze_source(
        source_path
    )

    all_drifts = []

    # ========================================================
    # DOCUMENTED ENDPOINT -> IMPLEMENTATION CHECKS
    # ========================================================

    for endpoint in contract.get(
        "endpoints",
        []
    ):

        source_route = (
            find_matching_source_route(
                endpoint,
                source.get("routes", [])
            )
        )

        if source_route is None:

            all_drifts.append({
                "endpoint":
                    endpoint["path"],

                "method":
                    endpoint["method"],

                "issue_type":
                    "missing_implementation_endpoint",

                "field_or_parameter":
                    None,

                "expected":
                    "endpoint implemented",

                "actual":
                    "endpoint not found",

                "evidence": {
                    "documented_endpoint":
                        endpoint["path"],

                    "documented_method":
                        endpoint["method"]
                }
            })

            continue

        # Response type mismatches
        all_drifts.extend(
            detect_response_type_drifts(
                endpoint,
                source_route
            )
        )

        # Response enum violations
        all_drifts.extend(
            detect_response_enum_drifts(
                endpoint,
                source_route
            )
        )

        # Query parameter type mismatches
        all_drifts.extend(
            detect_query_parameter_type_drifts(
                endpoint,
                source_route
            )
        )

        # Response status mismatches
        all_drifts.extend(
            detect_response_status_drifts(
                endpoint,
                source_route
            )
        )

        # Missing required response fields
        all_drifts.extend(
            detect_missing_response_fields(
                endpoint,
                source_route
            )
        )

        # Undocumented response fields
        all_drifts.extend(
            detect_extra_response_fields(
                endpoint,
                source_route
            )
        )

        # Path parameter mismatches
        all_drifts.extend(
            detect_parameter_type_drifts(
                endpoint,
                source_route
            )
        )

        # Error response schema mismatches
        all_drifts.extend(
            detect_error_response_schema_drifts(
                endpoint,
                source_route
            )
        )

    # ========================================================
    # IMPLEMENTED -> NOT DOCUMENTED CHECKS
    # ========================================================

    documented_routes = {
        (
            endpoint.get("normalized_path"),
            str(
                endpoint.get("method")
            ).upper()
        )
        for endpoint in contract.get(
            "endpoints",
            []
        )
    }

    for source_route in source.get(
        "routes",
        []
    ):

        source_path = source_route.get(
            "normalized_path"
        )

        for source_method in source_route.get(
            "methods",
            []
        ):

            source_method = str(
                source_method
            ).upper()

            if (
                source_path,
                source_method
            ) in documented_routes:
                continue

            all_drifts.append({
                "endpoint":
                    source_path,

                "method":
                    source_method,

                "issue_type":
                    "undocumented_implementation_endpoint",

                "field_or_parameter":
                    None,

                "expected":
                    "not documented",

                "actual":
                    "implemented",

                "severity":
                    "medium",

                "evidence": {
                    "source_path":
                        source_route.get(
                            "path"
                        ),

                    "source_normalized_path":
                        source_path,

                    "source_method":
                        source_method,

                    "documented":
                        False,

                    "implemented":
                        True
                }
            })

    return {
        "contract":
            contract,

        "source":
            source,

        "drifts":
            all_drifts
    }

if __name__ == "__main__":

    result = detect_drifts(
        "benchmark/case01/openapi.yaml",
        "benchmark/case01/app.py"
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )
