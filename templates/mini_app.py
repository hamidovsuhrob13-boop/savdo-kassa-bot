from flask import Flask, render_template, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"ok": True}


@app.route("/api/dashboard")
def dashboard():
    return jsonify({
        "products_count": 0,
        "total_items": 0,
        "stock_value": 0,
        "total_sales": 0,
        "total_debt": 0
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
