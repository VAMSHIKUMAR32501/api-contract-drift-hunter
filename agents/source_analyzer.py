import ast
import re
import sys
from pathlib import Path


HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}


# ============================================================
# ROUTE NORMALIZATION
# ============================================================

def normalize_route(route):
    """
    Convert Flask route parameters into a common format.

    /users/<int:user_id>
        -> /users/{param}

    /users/<user_id>
        -> /users/{param}
    """

    if not isinstance(route, str):
        return ""

    route = re.sub(
        r"<[^:>]+:[^>]+>",
        "{param}",
        route
    )

    route = re.sub(
        r"<[^>]+>",
        "{param}",
        route
    )

    return route


# ============================================================
# CONSTANT / TYPE HELPERS
# ============================================================

def get_constant_value(node):
    """
    Extract a simple Python constant.
    """

    if isinstance(node, ast.Constant):
        return node.value

    return None


def infer_python_type(value):
    """
    Convert a Python value into an API-style type.
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


def infer_ast_value_type(node):
    """
    Infer type directly from an AST expression.
    """

    if isinstance(node, ast.Constant):
        return infer_python_type(
            node.value
        )

    if isinstance(node, ast.List):
        return "array"

    if isinstance(node, ast.Dict):
        return "object"

    if isinstance(node, ast.Tuple):
        return "array"

    if isinstance(node, ast.Name):
        return "unknown"

    if isinstance(node, ast.Subscript):
        return "unknown"

    # ------------------------------------------
    # Function calls
    # ------------------------------------------

    if isinstance(node, ast.Call):

        # str(...)
        if (
            isinstance(
                node.func,
                ast.Name
            )
            and node.func.id == "str"
        ):
            return "string"

        # int(...)
        if (
            isinstance(
                node.func,
                ast.Name
            )
            and node.func.id == "int"
        ):
            return "integer"

        # float(...)
        if (
            isinstance(
                node.func,
                ast.Name
            )
            and node.func.id == "float"
        ):
            return "number"

        # bool(...)
        if (
            isinstance(
                node.func,
                ast.Name
            )
            and node.func.id == "bool"
        ):
            return "boolean"

        return "unknown"

    if isinstance(node, ast.BinOp):
        return "unknown"

    return "unknown"

# ============================================================
# EXPRESSION DESCRIPTION
# ============================================================

def describe_expression(node):
    """
    Produce a safe textual representation of an AST expression.

    This is used as evidence only. It does not pretend that
    an expression has a known runtime type.
    """

    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Constant):
        return repr(node.value)

    if isinstance(node, ast.Attribute):

        base = describe_expression(
            node.value
        )

        if base:
            return f"{base}.{node.attr}"

        return node.attr

    if isinstance(node, ast.Call):

        function = describe_expression(
            node.func
        )

        arguments = []

        for argument in node.args:

            arguments.append(
                describe_expression(
                    argument
                )
            )

        return (
            f"{function}"
            f"("
            f"{', '.join(arguments)}"
            f")"
        )

    if isinstance(node, ast.Subscript):

        base = describe_expression(
            node.value
        )

        key = describe_expression(
            node.slice
        )

        return f"{base}[{key}]"

    if isinstance(node, ast.Dict):
        return "dict"

    if isinstance(node, ast.List):
        return "list"

    return "<expression>"


# ============================================================
# DICTIONARY EXTRACTION
# ============================================================

def extract_dict_fields(dict_node):
    """
    Extract fields from a Python dictionary.
    """

    fields = {}

    if not isinstance(
        dict_node,
        ast.Dict
    ):
        return fields

    for key_node, value_node in zip(
        dict_node.keys,
        dict_node.values
    ):

        key = get_constant_value(
            key_node
        )

        if not isinstance(
            key,
            str
        ):
            continue

        # ------------------------------------------
        # Literal
        # ------------------------------------------

        value = get_constant_value(
            value_node
        )

        if value is not None:

            fields[key] = {
                "type":
                    infer_python_type(
                        value
                    ),

                "value":
                    value,

                "source_expression":
                    describe_expression(
                        value_node
                    ),
            }

            continue

        # ------------------------------------------
        # Name / variable
        # ------------------------------------------

        if isinstance(
            value_node,
            ast.Name
        ):

            fields[key] = {
                "type":
                    "unknown",

                "value":
                    value_node.id,

                "source_expression":
                    value_node.id,
            }

            continue

        # ------------------------------------------
        # Other expression
        # ------------------------------------------

        fields[key] = {
            "type":
                infer_ast_value_type(
                    value_node
                ),

            "value":
                None,

            "source_expression":
                describe_expression(
                    value_node
                ),
        }

    return fields


# ============================================================
# RETURN ANALYSIS
# ============================================================

# ============================================================
# RETURN ANALYSIS
# ============================================================

def extract_return_dict(
    function_node
):
    """
    Find jsonify({...}) or jsonify(variable)
    and extract response fields.

    Handles both:

        return jsonify({...})

    and:

        return jsonify({...}), 400
    """

    for node in ast.walk(
        function_node
    ):

        if not isinstance(
            node,
            ast.Return
        ):
            continue

        value = node.value

        # --------------------------------------------------
        # Direct jsonify(...)
        # --------------------------------------------------

        jsonify_call = None

        if isinstance(
            value,
            ast.Call
        ):

            jsonify_call = value

        # --------------------------------------------------
        # jsonify(...), STATUS
        # --------------------------------------------------

        elif isinstance(
            value,
            ast.Tuple
        ) and len(value.elts) >= 1:

            first = value.elts[0]

            if isinstance(
                first,
                ast.Call
            ):
                jsonify_call = first

        if jsonify_call is None:
            continue

        if not isinstance(
            jsonify_call.func,
            ast.Name
        ):
            continue

        if jsonify_call.func.id != "jsonify":
            continue

        if not jsonify_call.args:
            continue

        argument = jsonify_call.args[0]

        # --------------------------------------------------
        # Direct dictionary
        # --------------------------------------------------

        if isinstance(
            argument,
            ast.Dict
        ):

            return extract_dict_fields(
                argument
            )

        # --------------------------------------------------
        # Variable dictionary
        # --------------------------------------------------

        if isinstance(
            argument,
            ast.Name
        ):

            variable_name = (
                argument.id
            )

            for statement in ast.walk(
                function_node
            ):

                if not isinstance(
                    statement,
                    ast.Assign
                ):
                    continue

                if not isinstance(
                    statement.value,
                    ast.Dict
                ):
                    continue

                for target in statement.targets:

                    if (
                        isinstance(
                            target,
                            ast.Name
                        )
                        and target.id
                        == variable_name
                    ):

                        return extract_dict_fields(
                            statement.value
                        )

    return {}


# ============================================================
# REQUEST JSON VARIABLES
# ============================================================

def find_request_data_variables(
    function_node
):
    """
    Find variables containing Flask request JSON.

    Examples:

        data = request.get_json()

        data = request.get_json(silent=True) or {}

        data = request.json
    """

    variables = set()

    for node in ast.walk(
        function_node
    ):

        if not isinstance(
            node,
            ast.Assign
        ):
            continue

        value = node.value

        is_request_json = False

        # ------------------------------------------
        # request.get_json(...)
        # ------------------------------------------

        if isinstance(
            value,
            ast.Call
        ):

            if isinstance(
                value.func,
                ast.Attribute
            ):

                if (
                    value.func.attr
                    == "get_json"
                ):

                    if (
                        isinstance(
                            value.func.value,
                            ast.Name
                        )
                        and value.func.value.id
                        == "request"
                    ):
                        is_request_json = True

        # ------------------------------------------
        # request.json
        # ------------------------------------------

        elif isinstance(
            value,
            ast.Attribute
        ):

            if (
                value.attr == "json"
                and isinstance(
                    value.value,
                    ast.Name
                )
                and value.value.id
                == "request"
            ):

                is_request_json = True

        # ------------------------------------------
        # request.get_json(...) or {}
        # ------------------------------------------

        elif isinstance(
            value,
            ast.BoolOp
        ):

            for part in value.values:

                if not isinstance(
                    part,
                    ast.Call
                ):
                    continue

                if not isinstance(
                    part.func,
                    ast.Attribute
                ):
                    continue

                if part.func.attr != "get_json":
                    continue

                if (
                    isinstance(
                        part.func.value,
                        ast.Name
                    )
                    and part.func.value.id
                    == "request"
                ):
                    is_request_json = True

        if not is_request_json:
            continue

        for target in node.targets:

            if isinstance(
                target,
                ast.Name
            ):

                variables.add(
                    target.id
                )

    return variables


# ============================================================
# REQUEST FIELD EXTRACTION
# ============================================================

def extract_request_body_fields(
    function_node
):
    """
    Extract request-body field usage.

    Handles:

        data = request.get_json()

        data.get("quantity")

        data["quantity"]

        item = {
            "quantity": data.get("quantity")
        }

    Important:
    data.get("quantity") does NOT have a statically known
    Python type. We therefore record:

        type = unknown

    but preserve the data-flow evidence.
    """

    request_variables = (
        find_request_data_variables(
            function_node
        )
    )

    fields = {}

    for node in ast.walk(
        function_node
    ):

        # ==================================================
        # data.get("field")
        # ==================================================

        if isinstance(
            node,
            ast.Call
        ):

            if not isinstance(
                node.func,
                ast.Attribute
            ):
                continue

            if node.func.attr != "get":
                continue

            base = node.func.value

            if not (
                isinstance(
                    base,
                    ast.Name
                )
                and base.id in request_variables
            ):
                continue

            if not node.args:
                continue

            field_name = get_constant_value(
                node.args[0]
            )

            if not isinstance(
                field_name,
                str
            ):
                continue

            expression = (
                f'{base.id}.get("{field_name}")'
            )

            fields[field_name] = {
                "type":
                    "unknown",

                "value":
                    None,

                "source_expression":
                    expression,

                "request_source":
                    "json_body",

                "access":
                    "get",

                "nullable_from_source":
                    True,

                "statically_typed":
                    False,
            }

        # ==================================================
        # data["field"]
        # ==================================================

        elif isinstance(
            node,
            ast.Subscript
        ):

            base = node.value

            if not (
                isinstance(
                    base,
                    ast.Name
                )
                and base.id in request_variables
            ):
                continue

            field_name = get_constant_value(
                node.slice
            )

            if not isinstance(
                field_name,
                str
            ):
                continue

            expression = (
                f'{base.id}["{field_name}"]'
            )

            fields[field_name] = {
                "type":
                    "unknown",

                "value":
                    None,

                "source_expression":
                    expression,

                "request_source":
                    "json_body",

                "access":
                    "subscript",

                "nullable_from_source":
                    False,

                "statically_typed":
                    False,
            }

    return fields


# ============================================================
# ROUTE PARAMETERS
# ============================================================

def extract_route_parameters(
    route,
    function_node
):
    """
    Extract Flask route parameters.

    Example:

        /users/<int:user_id>

    becomes:

        {
            "user_id": {
                "type": "integer",
                "location": "path",
                "required": true
            }
        }
    """

    parameters = {}

    if not isinstance(
        route,
        str
    ):
        return parameters

    matches = re.findall(
        r"<([^>]+)>",
        route
    )

    argument_names = {
        arg.arg
        for arg in function_node.args.args
    }

    converter_types = {
        "int": "integer",
        "float": "number",
        "path": "string",
        "string": "string",
    }

    for match in matches:

        if ":" in match:

            converter, name = (
                match.split(
                    ":",
                    1
                )
            )

        else:

            converter = "string"
            name = match

        converter = converter.lower()

        parameter_type = (
            converter_types.get(
                converter,
                "string"
            )
        )

        parameters[name] = {
            "type":
                parameter_type,

            "location":
                "path",

            "required":
                name in argument_names,
        }

    return parameters

# ============================================================
# QUERY PARAMETER EXTRACTION
# ============================================================

def extract_query_parameters(function_node):
    """
    Extract Flask query parameter usage.

    Examples:

        request.args.get("limit")
        request.args["limit"]

    Flask request.args values are strings unless the
    implementation explicitly converts them.
    """

    parameters = {}

    for node in ast.walk(function_node):

        # ----------------------------------------------------
        # request.args.get("limit")
        # ----------------------------------------------------

        if isinstance(node, ast.Call):

            if not isinstance(
                node.func,
                ast.Attribute
            ):
                continue

            if node.func.attr != "get":
                continue

            base = node.func.value

            if not isinstance(
                base,
                ast.Attribute
            ):
                continue

            if base.attr != "args":
                continue

            if not isinstance(
                base.value,
                ast.Name
            ):
                continue

            if base.value.id != "request":
                continue

            if not node.args:
                continue

            name = get_constant_value(
                node.args[0]
            )

            if not isinstance(
                name,
                str
            ):
                continue

            parameters[name] = {
                "type":
                    "string",

                "location":
                    "query",

                "required":
                    False,

                "source_expression":
                    f'request.args.get("{name}")',

                "conversion":
                    None,
            }

        # ----------------------------------------------------
        # request.args["limit"]
        # ----------------------------------------------------

        elif isinstance(
            node,
            ast.Subscript
        ):

            base = node.value

            if not isinstance(
                base,
                ast.Attribute
            ):
                continue

            if base.attr != "args":
                continue

            if not isinstance(
                base.value,
                ast.Name
            ):
                continue

            if base.value.id != "request":
                continue

            name = get_constant_value(
                node.slice
            )

            if not isinstance(
                name,
                str
            ):
                continue

            parameters[name] = {
                "type":
                    "string",

                "location":
                    "query",

                "required":
                    True,

                "source_expression":
                    f'request.args["{name}"]',

                "conversion":
                    None,
            }

    return parameters
# ============================================================
# ROUTES
# ============================================================
# ============================================================
# RESPONSE STATUS EXTRACTION
# ============================================================

def extract_response_statuses(function_node):
    """
    Extract HTTP status codes returned by a Flask route.

    Handles patterns such as:

        return jsonify(data), 200

        if condition:
            return jsonify(data), 200

        return jsonify(error), 404

    The analyzer records the status code and a lightweight
    description of the surrounding condition.
    """

    responses = []

    def condition_text(node):
        if node is None:
            return None

        try:
            return ast.unparse(node)
        except Exception:
            return None

    def visit_statements(statements, condition=None):

        for statement in statements:

            # ------------------------------------------------
            # return jsonify(...), STATUS
            # ------------------------------------------------

            if isinstance(
                statement,
                ast.Return
            ):

                value = statement.value

                if isinstance(
                    value,
                    ast.Tuple
                ) and len(value.elts) >= 2:

                    status_node = value.elts[1]

                    status_code = (
                        get_constant_value(
                            status_node
                        )
                    )

                    if isinstance(
                        status_code,
                        int
                    ):

                        responses.append({
                            "status_code":
                                status_code,

                            "condition":
                                condition_text(
                                    condition
                                ),
                        })

                continue

            # ------------------------------------------------
            # if / else branches
            # ------------------------------------------------

            if isinstance(
                statement,
                ast.If
            ):

                # True branch
                visit_statements(
                    statement.body,
                    statement.test
                )

                # False / else branch
                if statement.orelse:

                    visit_statements(
                        statement.orelse,
                        None
                    )

                continue

            # ------------------------------------------------
            # Nested blocks
            # ------------------------------------------------

            if isinstance(
                statement,
                (
                    ast.For,
                    ast.While,
                    ast.With,
                    ast.Try
                )
            ):

                body = getattr(
                    statement,
                    "body",
                    []
                )

                visit_statements(
                    body,
                    condition
                )

                handlers = getattr(
                    statement,
                    "handlers",
                    []
                )

                for handler in handlers:

                    visit_statements(
                        handler.body,
                        condition
                    )

                final_body = getattr(
                    statement,
                    "finalbody",
                    []
                )

                visit_statements(
                    final_body,
                    condition
                )

    visit_statements(
        function_node.body
    )

    return responses
# ============================================================
# RESPONSE FIELDS BY STATUS
# ============================================================

def extract_response_fields_by_status(
    function_node
):
    """
    Extract jsonify response fields grouped by HTTP status.

    Handles both:

        return jsonify({...}), 200

    and:

        customer = {...}
        return jsonify(customer), 200

    Multiple branches using the same status code are kept
    separately.
    """

    responses = {}

    def add_response(
        status_code,
        fields
    ):
        key = str(status_code)

        if key not in responses:
            responses[key] = []

        responses[key].append(
            fields
        )

    # --------------------------------------------------------
    # Find dictionary assigned to a variable.
    # --------------------------------------------------------

    assigned_dicts = {}

    for node in ast.walk(
        function_node
    ):

        if not isinstance(
            node,
            ast.Assign
        ):
            continue

        if not isinstance(
            node.value,
            ast.Dict
        ):
            continue

        fields = extract_dict_fields(
            node.value
        )

        for target in node.targets:

            if isinstance(
                target,
                ast.Name
            ):

                assigned_dicts[
                    target.id
                ] = fields

    # --------------------------------------------------------
    # Inspect every return statement.
    # --------------------------------------------------------

    for node in ast.walk(
        function_node
    ):

        if not isinstance(
            node,
            ast.Return
        ):
            continue

        value = node.value

        jsonify_call = None
        status_code = None

        # ----------------------------------------------------
        # return jsonify(...), STATUS
        # ----------------------------------------------------

        if (
            isinstance(
                value,
                ast.Tuple
            )
            and len(value.elts) >= 2
        ):

            first = value.elts[0]
            second = value.elts[1]

            if isinstance(
                first,
                ast.Call
            ):
                jsonify_call = first

            status_code = (
                get_constant_value(
                    second
                )
            )

        # ----------------------------------------------------
        # return jsonify(...)
        # Flask defaults to 200.
        # ----------------------------------------------------

        elif isinstance(
            value,
            ast.Call
        ):

            jsonify_call = value

        if jsonify_call is None:
            continue

        if not isinstance(
            jsonify_call.func,
            ast.Name
        ):
            continue

        if jsonify_call.func.id != "jsonify":
            continue

        if not jsonify_call.args:
            continue

        # ----------------------------------------------------
        # Flask default status.
        # ----------------------------------------------------

        if status_code is None:
            status_code = 200

        if not isinstance(
            status_code,
            int
        ):
            continue

        argument = jsonify_call.args[0]

        # ----------------------------------------------------
        # Direct dictionary:
        #
        # return jsonify({
        #     "error": "..."
        # }), 400
        # ----------------------------------------------------

        if isinstance(
            argument,
            ast.Dict
        ):

            fields = extract_dict_fields(
                argument
            )

            add_response(
                status_code,
                fields
            )

            continue

        # ----------------------------------------------------
        # Variable dictionary:
        #
        # customer = {...}
        # return jsonify(customer), 200
        # ----------------------------------------------------

        if isinstance(
            argument,
            ast.Name
        ):

            variable_name = (
                argument.id
            )

            fields = assigned_dicts.get(
                variable_name
            )

            if fields is not None:

                add_response(
                    status_code,
                    fields
                )

    return responses
def extract_routes(tree):
    """
    Extract Flask routes and attached functions.
    """

    routes = []

    for node in tree.body:

        if not isinstance(
            node,
            ast.FunctionDef
        ):
            continue

        route = None
        methods = ["GET"]

        for decorator in node.decorator_list:

            if not isinstance(
                decorator,
                ast.Call
            ):
                continue

            if not isinstance(
                decorator.func,
                ast.Attribute
            ):
                continue

            if decorator.func.attr != "route":
                continue

            # ------------------------------------------
            # Route path
            # ------------------------------------------

            if decorator.args:

                route = get_constant_value(
                    decorator.args[0]
                )

            # ------------------------------------------
            # HTTP methods
            # ------------------------------------------

            for keyword in decorator.keywords:

                if keyword.arg != "methods":
                    continue

                if isinstance(
                    keyword.value,
                    ast.List
                ):

                    methods = []

                    for item in (
                        keyword.value.elts
                    ):

                        value = (
                            get_constant_value(
                                item
                            )
                        )

                        if isinstance(
                            value,
                            str
                        ):

                            methods.append(
                                value.upper()
                            )

        if route is None:
            continue

        response_fields = (
            extract_return_dict(
                node
            )
        )
        response_fields_by_status = (
            extract_response_fields_by_status(
               node
    )
)
        response_statuses = (
            extract_response_statuses(
            node
    )
)
        request_body_fields = (
            extract_request_body_fields(
                node
            )
        )

        routes.append({
            "path":
                route,

            "normalized_path":
                normalize_route(
                    route
                ),

            "methods":
                methods,

            "function":
                node.name,

            "parameters":
                extract_route_parameters(
                    route,
                    node
                ),

            "query_parameters":
                extract_query_parameters(
                  node
    ),

            "request_body_fields":
                request_body_fields,

            "response_fields":
                response_fields,
            "response_fields_by_status":
               response_fields_by_status,
            "response_statuses":
                response_statuses,
        })

    return routes


# ============================================================
# MAIN ANALYZER
# ============================================================

def analyze_source(
    source_path
):
    """
    Analyze a Python Flask API source file
    using AST.

    No LLM is used.
    """

    source_path = Path(
        source_path
    )

    source = source_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    return {
        "file":
            str(source_path),

        "language":
            "python",

        "framework":
            "flask",

        "routes":
            extract_routes(
                tree
            ),
    }


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    import json
    import sys

    # --------------------------------------------------------
    # Accept source file from command line.
    #
    # Example:
    #
    # python agents\source_analyzer.py benchmark\case03\app.py
    #
    # If no argument is supplied, use Case 11 as the default.
    # --------------------------------------------------------

    if len(sys.argv) >= 2:

        source_path = sys.argv[1]

    else:

        source_path = (
            "benchmark/case11/app.py"
        )

    result = analyze_source(
        source_path
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )