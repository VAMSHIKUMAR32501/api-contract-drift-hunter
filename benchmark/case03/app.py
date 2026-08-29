from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):

    if order_id == 1:
        order = {
            "id": 1,
            "status": "shipped"
        }

        return jsonify(order), 200

    return jsonify({
        "error": "Order not found"
    }), 200


if __name__ == "__main__":
    app.run(port=5002)