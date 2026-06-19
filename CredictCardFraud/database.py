import sqlite3
from datetime import datetime

DB_PATH = "fraud.db"


# ================= CREATE TABLES =================
def create_transactions_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        transaction_type TEXT,
        merchant_category TEXT,
        result TEXT,
        probability REAL,
        risk_score INTEGER,
        date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def create_user_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


# ================= SAVE TRANSACTION =================
def save_transaction(amount, transaction_type, merchant_category,
                     result, probability, risk_score):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO transactions 
    (amount, transaction_type, merchant_category, result, probability, risk_score, date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        amount,
        transaction_type,
        merchant_category,
        result,
        probability,
        risk_score,
        current_time
    ))

    conn.commit()
    conn.close()


# ================= GET ALL TRANSACTIONS =================
def get_all_transactions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # ✅ MUST be before cursor

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")

    rows = cursor.fetchall()
    conn.close()

    return rows


# ================= DASHBOARD STATS =================
def get_dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM transactions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE result='Fraud'")
    fraud = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE result='Genuine'")
    genuine = cursor.fetchone()[0]

    fraud_rate = (fraud / total * 100) if total > 0 else 0

    conn.close()

    return {
        "total": total,
        "fraud": fraud,
        "genuine": genuine,
        "fraud_rate": round(fraud_rate, 2)
    }