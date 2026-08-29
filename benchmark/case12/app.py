from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/ratings", methods=["POST"])
def submit_rating():
    data = request.get_json(silent=True) or {}

    rating = data.get("rating")

    return jsonify({
        "rating": rating,
        "status": "accepted"
    }), 201


if __name__ == "__main__":
    app.run(port=5011)