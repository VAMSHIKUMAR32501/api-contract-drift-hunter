from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = {
        "id": customer_id,
        "name": "John",
        "email": "john@example.com"
    }

    return jsonify(customer)


if __name__ == "__main__":
    app.run(port=5003)