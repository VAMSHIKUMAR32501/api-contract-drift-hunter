from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/profiles", methods=["POST"])
def create_profile():
    data = request.get_json(silent=True) or {}

    username = data.get("username")

    return jsonify({
        "username": username,
        "status": "created"
    }), 201


if __name__ == "__main__":
    app.run(port=5013)