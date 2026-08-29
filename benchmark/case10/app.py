from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):

    if customer_id == 1:
        customer = {
            "id": str(customer_id),
            "name": "Sarah",
            "age": "28",
            "status": "pending",
            "email": "sarah@example.com"
        }

        return jsonify(customer), 200

    return jsonify({
        "error": "Customer not found"
    }), 200


if __name__ == "__main__":
    app.run(port=5009)