import re
from pathlib import Path

import yaml


HTTP_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
    "trace",
}


def load_openapi(openapi_path):
    """
    Load an OpenAPI YAML file.
    """

    openapi_path = Path(openapi_path)

    with open(
        openapi_path,
        "r",
        encoding="utf-8"
    ) as f:
        return yaml.safe_load(f)


def normalize_path(path):
    """
    Normalize OpenAPI path parameters.

    Example:

        /users/{id}

    becomes:

        /users/{param}
    """

    if not isinstance(path, str):
        return ""

    return re.sub(
        r"\{[^}]+\}",
        "{param}",
        path.strip()
    )


def extract_parameters(operation):
    """
    Extract parameters from an OpenAPI operation.
    """

    parameters = []

    for parameter in operation.get(
        "parameters",
        []
    ):

        schema = parameter.get(
            "schema",
            {}
        )

        parameters.append({
            "name": parameter.get(
                "name"
            ),

            "in": parameter.get(
                "in"
            ),

            "required": parameter.get(
                "required",
                False
            ),

            "type": schema.get(
                "type"
            ),

            "format": schema.get(
                "format"
            ),

            "enum": schema.get(
                "enum"
            ),

            "minimum": schema.get(
                "minimum"
            ),

            "maximum": schema.get(
                "maximum"
            ),

            "minLength": schema.get(
                "minLength"
            ),

            "maxLength": schema.get(
                "maxLength"
            ),

            "minItems": schema.get(
                "minItems"
            ),

            "maxItems": schema.get(
                "maxItems"
            ),
        })

    return parameters


def extract_schema_properties(schema):
    """
    Extract object properties and their constraints.
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

    result = {}

    for name, property_schema in properties.items():

        if not isinstance(
            property_schema,
            dict
        ):
            property_schema = {}

        result[name] = {
            "type": property_schema.get(
                "type"
            ),

            "format": property_schema.get(
                "format"
            ),

            "required": name in required,

            "nullable": property_schema.get(
                "nullable",
                False
            ),

            "enum": property_schema.get(
                "enum"
            ),

            "minimum": property_schema.get(
                "minimum"
            ),

            "maximum": property_schema.get(
                "maximum"
            ),

            "minLength": property_schema.get(
                "minLength"
            ),

            "maxLength": property_schema.get(
                "maxLength"
            ),

            "minItems": property_schema.get(
                "minItems"
            ),

            "maxItems": property_schema.get(
                "maxItems"
            ),
        }

    return result


def extract_responses(operation):
    """
    Extract documented response information.
    """

    responses = {}

    for status_code, response in operation.get(
        "responses",
        {}
    ).items():

        response_info = {
            "description": response.get(
                "description",
                ""
            ),
            "content_type": None,
            "schema_type": None,
            "properties": {},
        }

        content = response.get(
            "content",
            {}
        )

        if content:

            # Usually application/json.
            content_type = next(
                iter(content)
            )

            response_info[
                "content_type"
            ] = content_type

            media_type = content[
                content_type
            ]

            schema = media_type.get(
                "schema",
                {}
            )

            response_info[
                "schema_type"
            ] = schema.get(
                "type"
            )

            response_info[
                "properties"
            ] = extract_schema_properties(
                schema
            )

        responses[str(status_code)] = (
            response_info
        )

    return responses

def extract_request_body(operation):
    """
    Extract the documented request body from OpenAPI.
    """

    request_body = operation.get(
        "requestBody"
    )

    if not request_body:
        return None

    content = request_body.get(
        "content",
        {}
    )

    if not content:
        return None

    if "application/json" in content:
        media_type = content[
            "application/json"
        ]
    else:
        content_type = next(
            iter(content)
        )

        media_type = content[
            content_type
        ]

    schema = media_type.get(
        "schema",
        {}
    )

    return {
        "required": request_body.get(
            "required",
            False
        ),

        "content_type": (
            "application/json"
            if "application/json" in content
            else next(iter(content))
        ),

        "schema_type":
            schema.get("type"),

        "properties":
            extract_schema_properties(
                schema
            ),
    }

def extract_contract(openapi_path):
    """
    Convert the OpenAPI specification into
    a simple machine-readable contract.

    This is intentionally deterministic.
    No LLM is used here.
    """

    spec = load_openapi(
        openapi_path
    )

    contract = {
        "title": spec.get(
            "info",
            {}
        ).get(
            "title"
        ),

        "version": spec.get(
            "info",
            {}
        ).get(
            "version"
        ),

        "endpoints": []
    }

    paths = spec.get(
        "paths",
        {}
    )

    for path, path_item in paths.items():

        for method, operation in path_item.items():

            if method.lower() not in HTTP_METHODS:
                continue

            endpoint = {
                "path": path,

                "normalized_path":
                    normalize_path(path),

                "method":
                    method.upper(),

                "summary":
                    operation.get(
                        "summary"
                    ),

                "parameters":
                    extract_parameters(
                        operation
                    ),

                "responses":
                    extract_responses(
                        operation
                    ),
                "request_body":
                 extract_request_body(
                 operation
                 ),
            }

            contract[
                "endpoints"
            ].append(endpoint)

    return contract


if __name__ == "__main__":

    contract = extract_contract(
        "benchmark/case11/openapi.yaml"
    )

    import json

    print(
        json.dumps(
            contract,
            indent=2
        )
    )