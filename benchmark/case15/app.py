from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/products", methods=["GET"])
def get_products():
    return jsonify([
        "Laptop",
        "Phone",
        "Keyboard"
    ])


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    return jsonify({
        "id": product_id,
        "name": "Laptop"
    })


# This endpoint is intentionally NOT documented in OpenAPI.
@app.route("/admin/export", methods=["GET"])
def admin_export():
    return jsonify({
        "status": "export ready",
        "records": 100
    })


if __name__ == "__main__":
    app.run(port=5014)