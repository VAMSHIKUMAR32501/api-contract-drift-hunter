import sys
from pathlib import Path
import json


# --------------------------------------------------
# Project root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.contract_extractor import extract_contract


# --------------------------------------------------
# Value generation
# --------------------------------------------------

def choose_example_value(schema):
    """
    Generate a safe value from an OpenAPI schema.
    """

    if not isinstance(schema, dict):
        return None

    # Explicit example
    if "example" in schema:
        return schema["example"]

    # Default
    if "default" in schema:
        return schema["default"]

    # Enum
    enum = schema.get("enum")

    if enum:
        return enum[0]

    schema_type = schema.get("type")

    # Integer
    if schema_type == "integer":

        minimum = schema.get("minimum")

        if minimum is not None:
            return minimum

        return 1

    # Number
    if schema_type == "number":

        minimum = schema.get("minimum")

        if minimum is not None:
            return minimum

        return 1.0

    # Boolean
    if schema_type == "boolean":
        return True

    # String
    if schema_type == "string":

        min_length = schema.get(
            "minLength",
        )
        if min_length is None:
            min_length=0

        if min_length > 0:
            return "a" * min_length

        return "test"

    # Array
    if schema_type == "array":

        min_items = schema.get(
            "minItems",
            0
        )

        item_schema = schema.get(
            "items",
            {}
        )

        item = choose_example_value(
            item_schema
        )

        return [
            item
            for _ in range(min_items)
        ]

    # Object
    if schema_type == "object":
        return generate_object_body(
            schema
        )

    return None


# --------------------------------------------------
# Object body
# --------------------------------------------------

def generate_object_body(schema):
    """
    Generate a JSON object using the
    documented OpenAPI properties.
    """

    if not isinstance(schema, dict):
        return {}

    properties = schema.get(
        "properties",
        {}
    )

    required = set(
        schema.get(
            "required",
            []
        )
    )

    body = {}

    for name, property_schema in properties.items():

        # Include required fields.
        if name in required:

            body[name] = choose_example_value(
                property_schema
            )

    return body


# --------------------------------------------------
# Path parameters
# --------------------------------------------------

def generate_path_parameters(endpoint):
    """
    Generate values for path parameters.
    """

    parameters = {}

    for parameter in endpoint.get(
        "parameters",
        []
    ):

        if parameter.get("in") != "path":
            continue

        name = parameter.get(
            "name"
        )

        parameters[name] = choose_example_value(
            parameter
        )

    return parameters


# --------------------------------------------------
# Query parameters
# --------------------------------------------------

def generate_query_parameters(endpoint):
    """
    Generate values for required query parameters.
    """

    parameters = {}

    for parameter in endpoint.get(
        "parameters",
        []
    ):

        if parameter.get("in") != "query":
            continue

        if not parameter.get(
            "required",
            False
        ):
            continue

        name = parameter.get(
            "name"
        )

        parameters[name] = choose_example_value(
            parameter
        )

    return parameters


# --------------------------------------------------
# Request body
# --------------------------------------------------

def generate_request_body(endpoint):
    """
    Generate a JSON request body from the
    extracted request_body information.
    """

    request_body = endpoint.get(
        "request_body"
    )

    if not request_body:
        return None

    properties = request_body.get(
        "properties",
        {}
    )

    body = {}

    for name, property_schema in properties.items():

        if property_schema.get(
            "required",
            False
        ):

            body[name] = choose_example_value(
                property_schema
            )

    return body


# --------------------------------------------------
# URL construction
# --------------------------------------------------

def build_concrete_path(
    endpoint,
    path_parameters
):
    """
    Replace OpenAPI path parameters with
    concrete values.

    Example:

        /users/{id}

    becomes:

        /users/1
    """

    path = endpoint.get(
        "path",
        ""
    )

    for name, value in path_parameters.items():

        path = path.replace(
            "{" + name + "}",
            str(value)
        )

    return path


# --------------------------------------------------
# Generate one request
# --------------------------------------------------

def generate_request(endpoint):
    """
    Generate a complete request description.
    """

    path_parameters = (
        generate_path_parameters(
            endpoint
        )
    )

    query_parameters = (
        generate_query_parameters(
            endpoint
        )
    )

    body = generate_request_body(
        endpoint
    )

    concrete_path = build_concrete_path(
        endpoint,
        path_parameters
    )

    return {
        "method": endpoint.get(
            "method",
            "GET"
        ),

        "path": endpoint.get(
            "path",
            ""
        ),

        "concrete_path":
            concrete_path,

        "path_parameters":
            path_parameters,

        "query_parameters":
            query_parameters,

        "json":
            body,
    }


# --------------------------------------------------
# Generate requests for contract
# --------------------------------------------------

def generate_requests(contract):
    """
    Generate one request for every endpoint.
    """

    requests = []

    for endpoint in contract.get(
        "endpoints",
        []
    ):

        requests.append(
            generate_request(
                endpoint
            )
        )

    return requests


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "Generating request for Case 11..."
    )

    contract = extract_contract(
        "benchmark/case11/openapi.yaml"
    )

    requests = generate_requests(
        contract
    )

    print()

    print(
        json.dumps(
            requests,
            indent=2
        )
    )