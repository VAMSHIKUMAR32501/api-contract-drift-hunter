from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/payments", methods=["POST"])
def create_payment():
    data = request.get_json(silent=True) or {}

    if "amount" not in data:
        return jsonify({
            "message": "Amount is required"
        }), 400

    return jsonify({
        "id": 101,
        "status": "created"
    }), 201


if __name__ == "__main__":
    app.run(port=5008)