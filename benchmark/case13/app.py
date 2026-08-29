from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/articles", methods=["POST"])
def create_article():
    data = request.get_json(silent=True) or {}

    article = {
        "title": data.get("title"),
        "tags": data.get("tags")
    }

    return jsonify(article), 201


if __name__ == "__main__":
    app.run(port=5012)