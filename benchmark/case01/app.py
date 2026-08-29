from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = {
        "id": user_id,
        "name": "Alice",
        "age": "25"
    }

    return jsonify(user)


if __name__ == "__main__":
    app.run(port=5000)