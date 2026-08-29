from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order_status(order_id):
    order = {
        "id": order_id,
        "status": "processing"
    }

    return jsonify(order)


if __name__ == "__main__":
    app.run(port=5006)