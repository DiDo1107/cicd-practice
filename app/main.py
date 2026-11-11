import os

from flask import Flask, jsonify, request

VERSION = os.getenv("APP_VERSION", "dev")

app = Flask(__name__)


def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


@app.route("/")
def index():
    return jsonify(message="Hello from CI/CD practice!", version=VERSION)


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/add")
def add_endpoint():
    try:
        a = float(request.args.get("a", 0))
        b = float(request.args.get("b", 0))
    except ValueError:
        return jsonify(error="a and b must be numbers"), 400
    return jsonify(result=add(a, b))


if __name__ == "__main__":
    # Dev-сервер; в Docker/Heroku приложение запускается через gunicorn
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 5000)))
