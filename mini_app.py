from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/api/dashboard")
def dashboard():
    return jsonify({
        "products_count": 0,
        "total_items": 0,
        "stock_value": 0,
        "total_sales": 0,
        "total_debt": 0
    })
