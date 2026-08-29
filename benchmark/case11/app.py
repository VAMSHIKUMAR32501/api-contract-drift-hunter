from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/cart/items", methods=["POST"])
def add_item():
    data = request.get_json(silent=True) or {}

    item = {
        "product_id": data.get("product_id"),
        "quantity": data.get("quantity")
    }

    return jsonify(item), 201


if __name__ == "__main__":
    app.run(port=5010)