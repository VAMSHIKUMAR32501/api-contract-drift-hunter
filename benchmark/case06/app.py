from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}

    user = {
        "name": data.get("name"),
        "email": data.get("email")
    }

    return jsonify(user), 201


if __name__ == "__main__":
    app.run(port=5005)