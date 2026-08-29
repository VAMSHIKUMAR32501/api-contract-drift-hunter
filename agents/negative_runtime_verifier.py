import json
import sys
import time
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.contract_extractor import extract_contract
from agents.negative_test_generator import (
    generate_negative_tests_for_contract
)


def build_url(
    base_url,
    path
):
    return (
        base_url.rstrip("/")
        + "/"
        + path.lstrip("/")
    )


def run_negative_test(
    test,
    base_url
):
    """
    Execute one intentionally invalid request.
    """

    method = test.get(
        "method",
        "GET"
    ).upper()

    path = test.get(
        "path",
        ""
    )

    body = test.get(
        "body"
    )

    url = build_url(
        base_url,
        path
    )

    started = time.perf_counter()

    try:

        response = requests.request(
            method=method,
            url=url,
            json=body,
            timeout=10
        )

        elapsed_ms = (
            time.perf_counter() - started
        ) * 1000

        try:
            response_body = response.json()

        except ValueError:
            response_body = None

        # A 4xx response means the API rejected
        # the invalid request.
        rejected = (
            400 <= response.status_code < 500
        )

        return {
            "method": method,
            "endpoint": path,
            "url": response.url,

            "test_type":
                test.get(
                    "test_type"
                ),

            "field":
                test.get(
                    "field"
                ),

            "request_body":
                body,

            "status_code":
                response.status_code,

            "response_body":
                response_body,

            "response_time_ms":
                round(
                    elapsed_ms,
                    2
                ),

            "rejected":
                rejected,

            "validation_enforced":
                rejected,

            "error":
                None,
        }

    except requests.RequestException as exc:

        return {
            "method": method,
            "endpoint": path,
            "url": url,

            "test_type":
                test.get(
                    "test_type"
                ),

            "field":
                test.get(
                    "field"
                ),

            "request_body":
                body,

            "status_code":
                None,

            "response_body":
                None,

            "response_time_ms":
                None,

            "rejected":
                False,

            "validation_enforced":
                False,

            "error":
                str(exc),
        }


def verify_negative_tests(
    contract,
    base_url
):
    """
    Execute all generated negative tests.
    """

    tests = (
        generate_negative_tests_for_contract(
            contract
        )
    )

    results = []

    for test in tests:

        result = run_negative_test(
            test,
            base_url
        )

        results.append(
            result
        )

    return {
        "base_url":
            base_url,

        "total_tests":
            len(results),

        "results":
            results,
    }


if __name__ == "__main__":

    print(
        "Running negative runtime verification..."
    )

    contract = extract_contract(
        "benchmark/case11/openapi.yaml"
    )

    result = verify_negative_tests(
        contract,
        "http://127.0.0.1:5010"
    )

    print()

    print(
        json.dumps(
            result,
            indent=2
        )
    )