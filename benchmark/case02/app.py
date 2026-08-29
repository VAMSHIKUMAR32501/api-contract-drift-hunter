from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = {
        "id": product_id,
        "name": "Laptop"
    }

    return jsonify(product)


if __name__ == "__main__":
    app.run(port=5001)