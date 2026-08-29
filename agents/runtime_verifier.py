import json
import sys
import time
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.contract_extractor import extract_contract
from agents.request_generator import generate_requests


def infer_json_type(value):
    """
    Infer the API/JSON type of a runtime value.
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


def extract_runtime_fields(body):
    """
    Extract runtime response fields and their
    observed JSON types.
    """

    if not isinstance(body, dict):
        return {}

    fields = {}

    for name, value in body.items():

        fields[name] = {
            "type":
                infer_json_type(value),

            "value":
                value,

            "is_null":
                value is None,
        }

    return fields


def build_concrete_path(
    path,
    path_parameters
):
    """
    Replace OpenAPI path parameters with
    generated concrete values.

    Example:

        /users/{id}

    becomes:

        /users/1
    """

    concrete_path = path

    for name, value in (
        path_parameters.items()
    ):

        concrete_path = concrete_path.replace(
            "{" + name + "}",
            str(value)
        )

    return concrete_path


def verify_request(
    request_data,
    base_url
):
    """
    Execute one generated request.
    """

    method = request_data.get(
        "method",
        "GET"
    ).upper()

    path = request_data.get(
        "path",
        ""
    )

    path_parameters = request_data.get(
        "path_parameters",
        {}
    )

    query_parameters = request_data.get(
        "query_parameters",
        {}
    )

    json_body = request_data.get(
        "json"
    )

    concrete_path = build_concrete_path(
        path,
        path_parameters
    )

    url = (
        base_url.rstrip("/")
        + "/"
        + concrete_path.lstrip("/")
    )

    started = time.perf_counter()

    try:

        response = requests.request(
            method=method,
            url=url,
            params=query_parameters,
            json=json_body,
            timeout=10
        )

        elapsed_ms = (
            time.perf_counter() - started
        ) * 1000

        try:
            body = response.json()

        except ValueError:
            body = None

        return {
            "endpoint":
                path,

            "method":
                method,

            "url":
                response.url,

            "request": {
                "path_parameters":
                    path_parameters,

                "query_parameters":
                    query_parameters,

                "json":
                    json_body,
            },

            "status_code":
                response.status_code,

            "response_time_ms":
                round(
                    elapsed_ms,
                    2
                ),

            "content_type":
                response.headers.get(
                    "Content-Type"
                ),

            "body":
                body,

            "body_type":
                infer_json_type(body),

            "fields":
                extract_runtime_fields(
                    body
                ),

            "error":
                None,
        }

    except requests.RequestException as exc:

        return {
            "endpoint":
                path,

            "method":
                method,

            "url":
                url,

            "request": {
                "path_parameters":
                    path_parameters,

                "query_parameters":
                    query_parameters,

                "json":
                    json_body,
            },

            "status_code":
                None,

            "response_time_ms":
                None,

            "content_type":
                None,

            "body":
                None,

            "body_type":
                "unknown",

            "fields":
                {},

            "error":
                str(exc),
        }


def verify_contract(
    contract,
    base_url="http://127.0.0.1:5000"
):
    """
    Generate valid requests from the contract
    and execute them against the running API.
    """

    generated_requests = (
        generate_requests(
            contract
        )
    )

    results = []

    for request_data in generated_requests:

        result = verify_request(
            request_data,
            base_url
        )

        results.append(
            result
        )

    return {
        "base_url":
            base_url,

        "requests":
            generated_requests,

        "results":
            results,
    }


if __name__ == "__main__":

    print(
        "Running runtime verification..."
    )

    contract = extract_contract(
        "benchmark/case11/openapi.yaml"
    )

    result = verify_contract(
        contract,
         base_url="http://127.0.0.1:5010"
    )

    print()

    print(
        json.dumps(
            result,
            indent=2
        )
    )