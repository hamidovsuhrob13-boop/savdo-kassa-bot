import os
import sqlite3

from flask import Flask, jsonify, render_template
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINI_APP_URL = os.getenv("MINI_APP_URL", "").strip()
DB_PATH = "savdo.db"

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        buy_price REAL DEFAULT 0,
        sell_price REAL DEFAULT 0,
        quantity INTEGER DEFAULT 0,
        note TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone TEXT,
        note TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        client_id INTEGER,
        qty INTEGER DEFAULT 1,
        sell_price REAL DEFAULT 0,
        total REAL DEFAULT 0,
        paid_now REAL DEFAULT 0,
        debt REAL DEFAULT 0,
        seller_name TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dashboard")
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products")
    products_count = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(quantity), 0) FROM products")
    total_items = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(quantity * buy_price), 0) FROM products")
    stock_value = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(total), 0) FROM sales")
    total_sales = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(debt), 0) FROM sales")
    total_debt = cur.fetchone()[0]

    conn.close()

    return jsonify({
        "products_count": products_count,
        "total_items": total_items,
        "stock_value": stock_value,
        "total_sales": total_sales,
        "total_debt": total_debt
    })


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Салом! Система запущена.\n\n"
        "Команды:\n"
        "/start — открыть меню\n"
        "/id — узнать свой Telegram ID"
    )

    if MINI_APP_URL:
        keyboard = [
            [KeyboardButton("Открыть систему", web_app=WebAppInfo(url=MINI_APP_URL))]
        ]
        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
    else:
        await update.message.reply_text(
            text + "\n\nMini App URL пока не задан."
        )


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Твой Telegram ID: {user.id}\nИмя: {user.full_name}"
    )


@app.route("/health")
def health():
    return {"ok": True}


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found")

    init_db()

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("id", get_id))

    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()