import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_endpoint(endpoint):
    """
    Normalize endpoint representations.

    Handles:

        POST /cart/items
        /cart/items

        GET /users/<int:user_id>
        /users/{id}
        /users/{user_id}
        /users/1

    All are normalized to the path only,
    with parameters represented as {param}.
    """

    if not isinstance(endpoint, str):
        return ""

    endpoint = endpoint.strip()

    # --------------------------------------------------------
    # Remove HTTP method prefix if present.
    #
    # POST /cart/items
    #     -> /cart/items
    #
    # GET /users/{id}
    #     -> /users/{id}
    # --------------------------------------------------------

    endpoint = re.sub(
        r"^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+",
        "",
        endpoint,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Flask typed parameter
    #
    # /users/<int:user_id>
    #     -> /users/{param}
    # --------------------------------------------------------

    endpoint = re.sub(
        r"<[^:>]+:[^>]+>",
        "{param}",
        endpoint
    )

    # --------------------------------------------------------
    # Flask untyped parameter
    #
    # /users/<user_id>
    #     -> /users/{param}
    # --------------------------------------------------------

    endpoint = re.sub(
        r"<[^>]+>",
        "{param}",
        endpoint
    )

    # --------------------------------------------------------
    # OpenAPI parameters
    #
    # /users/{id}
    # /users/{user_id}
    #     -> /users/{param}
    # --------------------------------------------------------

    endpoint = re.sub(
        r"\{[^}]+\}",
        "{param}",
        endpoint
    )

    # --------------------------------------------------------
    # Concrete numeric ID
    #
    # /users/1
    # /users/999
    #     -> /users/{param}
    # --------------------------------------------------------

    endpoint = re.sub(
        r"/\d+$",
        "/{param}",
        endpoint
    )

    # --------------------------------------------------------
    # Remove trailing slash except root
    # --------------------------------------------------------

    if len(endpoint) > 1:
        endpoint = endpoint.rstrip("/")

    return endpoint


def load_expected(case_path):
    return load_json(case_path / "expected.json")


def extract_predicted_issues(baseline_result):
    """
    Extract the issues list from the model's JSON response.
    """

    if not isinstance(baseline_result, str):
        return []

    text = baseline_result.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, dict):
        return []

    issues = data.get("issues", [])

    if not isinstance(issues, list):
        return []

    return issues


def issue_matches_expected(issue, expected):
    """
    Determine whether a predicted issue represents
    the expected contract drift.
    """

    if not isinstance(issue, dict):
        return False

    issue_type = str(
        issue.get("issue_type", "")
    ).lower().strip()

    field = str(
        issue.get("field_or_parameter", "")
    ).lower().strip()

    endpoint = normalize_endpoint(
        str(issue.get("endpoint", ""))
    )

    expected_endpoint = normalize_endpoint(
        str(expected.get("endpoint", ""))
    )

       # Case 01
    if expected.get("case_id") == "case01":

        expected_value = str(
            issue.get("expected", "")
        ).strip().lower()

        actual_value = str(
            issue.get("actual", "")
        ).strip().lower()

        field_value = str(
            issue.get("field_or_parameter", "")
        ).strip().lower()

        return (
            field_value == "age"
            and expected_value == "integer"
            and actual_value == "string"
        )
    # -------------------------------------------------
    # CASE 02
    # -------------------------------------------------
    if expected.get("case_id") == "case02":

        return (
            endpoint == expected_endpoint
            and field == "price"
            and (
                "missing" in issue_type
                or "required" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 03
    # -------------------------------------------------
    if expected.get("case_id") == "case03":

        return (
            endpoint == expected_endpoint
            and "status" in issue_type
            and "mismatch" in issue_type
        )

    # -------------------------------------------------
    # CASE 04
    # -------------------------------------------------
    if expected.get("case_id") == "case04":

        return (
            endpoint == expected_endpoint
            and field == "email"
            and (
                "undocumented" in issue_type
                or "extra" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 05
    # -------------------------------------------------
    if expected.get("case_id") == "case05":

        return (
            endpoint == expected_endpoint
            and field in {
                "limit",
                "limit parameter"
            }
            and (
                "mismatch" in issue_type
                or "type" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 06
    # -------------------------------------------------
    if expected.get("case_id") == "case06":

        return (
            endpoint == expected_endpoint
            and field == "email"
            and (
                "validation" in issue_type
                or "missing" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 07
    # -------------------------------------------------
    if expected.get("case_id") == "case07":

        return (
            endpoint == expected_endpoint
            and field == "status"
            and (
                "enum" in issue_type
                or "mismatch" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 08
    # -------------------------------------------------
    if expected.get("case_id") == "case08":

        return (
            endpoint == expected_endpoint
            and field == "department"
            and (
                "null" in issue_type
                or "type" in issue_type
                or "mismatch" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 09
    # -------------------------------------------------
    if expected.get("case_id") == "case09":

        return (
            endpoint == expected_endpoint
            and "mismatch" in issue_type
            and (
                "error" in issue_type
                or "schema" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 10
    # -------------------------------------------------
    if expected.get("case_id") == "case10":
        return False

    # -------------------------------------------------
    # CASE 11
    # -------------------------------------------------
    if expected.get("case_id") == "case11":

        return (
            endpoint == expected_endpoint
            and field == "quantity"
            and (
                "type" in issue_type
                or "mismatch" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 12
    # -------------------------------------------------
    if expected.get("case_id") == "case12":

        return (
            endpoint == expected_endpoint
            and field == "rating"
            and (
                "constraint" in issue_type
                or "validation" in issue_type
                or "mismatch" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 13
    # -------------------------------------------------
    if expected.get("case_id") == "case13":

        return (
            endpoint == expected_endpoint
            and field == "tags"
            and (
                "constraint" in issue_type
                or "array" in issue_type
                or "validation" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 14
    # -------------------------------------------------
    if expected.get("case_id") == "case14":

        return (
            endpoint == expected_endpoint
            and field == "username"
            and (
                "constraint" in issue_type
                or "string" in issue_type
                or "validation" in issue_type
            )
        )

    # -------------------------------------------------
    # CASE 15
    # -------------------------------------------------
    if expected.get("case_id") == "case15":

        issue_endpoint = str(
            issue.get("endpoint", "")
        ).lower()

        return (
            "/admin/export" in issue_endpoint
            and (
                "undocumented" in issue_type
                or "missing" in issue_type
            )
        )

    return False

def evaluate_case(case_number, baseline_result):

    case_path = (
        PROJECT_ROOT
        / "benchmark"
        / f"case{case_number:02d}"
    )

    expected = load_expected(case_path)

    predicted_issues = extract_predicted_issues(
        baseline_result
    )

    # -------------------------------------------------
    # CASE 10
    # Multiple expected drifts
    # -------------------------------------------------

    if expected["case_id"] == "case10":

        expected_drifts = expected["drifts"]

        matched = []

        for drift in expected_drifts:

            found = False

            for issue in predicted_issues:

                issue_text = json.dumps(
                    issue
                ).lower()

                if drift["type"] == "response_type_mismatch":

                    if (
                        drift["field"].lower()
                        in issue_text
                        and drift["expected"].lower()
                        in issue_text
                        and drift["actual"].lower()
                        in issue_text
                    ):
                        found = True

                elif drift["type"] == "enum_mismatch":

                    if (
                        drift["field"].lower()
                        in issue_text
                        and drift["actual"].lower()
                        in issue_text
                    ):
                        found = True

                elif drift["type"] == "undocumented_field":

                    if (
                        drift["field"].lower()
                        in issue_text
                        and "undocumented" in issue_text
                    ):
                        found = True

                elif drift["type"] == "status_code_mismatch":

                    if (
                        "404" in issue_text
                        and "200" in issue_text
                    ):
                        found = True

            matched.append(found)

        true_positives = sum(matched)

        expected_count = len(
            expected_drifts
        )

    else:

        true_positives = 0

        for issue in predicted_issues:

            if issue_matches_expected(
                issue,
                expected
            ):
                true_positives += 1
                break

        expected_count = 1

    false_positives = max(
        0,
        len(predicted_issues)
        - true_positives
    )

    false_negatives = max(
        0,
        expected_count
        - true_positives
    )

    precision = (
        true_positives
        / (true_positives + false_positives)
        if true_positives + false_positives > 0
        else 0
    )

    recall = (
        true_positives
        / (true_positives + false_negatives)
        if true_positives + false_negatives > 0
        else 0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if precision + recall > 0
        else 0
    )

    return {
        "case_id": expected["case_id"],
        "expected_drifts": expected_count,
        "predicted_issues": len(predicted_issues),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3)
    }


if __name__ == "__main__":
    print("Evaluator module loaded successfully.")