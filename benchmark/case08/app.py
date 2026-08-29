from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/employees/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):
    employee = {
        "id": employee_id,
        "name": "David",
        "department": None
    }

    return jsonify(employee)


if __name__ == "__main__":
    app.run(port=5007)