from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/products", methods=["GET"])
def search_products():
    limit = request.args.get("limit")

    products = [
        "Laptop",
        "Phone",
        "Keyboard",
        "Mouse",
        "Monitor"
    ]

    return jsonify({
        "limit": limit,
        "products": products[:3]
    })


if __name__ == "__main__":
    app.run(port=5004)