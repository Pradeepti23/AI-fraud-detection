# ==========================================================
# IMPORTS
# ==========================================================

from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import joblib
import random
import numpy as np
import smtplib
import threading
from email.mime.text import MIMEText

from database import (
    save_transaction,
    get_dashboard_stats,
    create_transactions_table,
    create_user_table
)
from dotenv import load_dotenv
load_dotenv()

import os
os.environ["EMAIL_USER"] = "creditproject28@gmail.com"
os.environ["EMAIL_PASS"] = "wcli uyca wlln kelv"
# ==========================================================
# INIT DB
# ==========================================================

create_transactions_table()
create_user_table()

DB_PATH = "fraud.db"

# ==========================================================
# FLASK APP
# ==========================================================

app = Flask(__name__)
app.secret_key = "fraud_detection_secret_key"

# ==========================================================
# FETCH TRANSACTIONS (ONLY ONE VERSION - FIXED)
# ==========================================================

def get_all_transactions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")

    rows = cursor.fetchall()
    conn.close()

    return rows

# ==========================================================
# LOAD MODELS (SAFE LOADING)
# ==========================================================

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

rf_model = joblib.load(os.path.join(BASE_DIR, "model", "random_forest.pkl"))
xgb_model = joblib.load(os.path.join(BASE_DIR, "model", "xgboost_fraud.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "model", "scaler.pkl"))
encoders = joblib.load(os.path.join(BASE_DIR, "model", "label_encoders.pkl"))

try:
    rf_model = joblib.load(os.path.join(BASE_DIR, "model", "random_forest.pkl"))
    xgb_model = joblib.load(os.path.join(BASE_DIR, "model", "xgboost_fraud.pkl"))
    scaler = joblib.load(os.path.join(BASE_DIR, "model", "scaler.pkl"))
    encoders = joblib.load(os.path.join(BASE_DIR, "model", "label_encoders.pkl"))

except Exception as e:
    print("MODEL LOAD ERROR:")
    print(e)
    rf_model = None
    xgb_model = None
    scaler = None
    encoders = {}

# ==========================================================
# EMAIL OTP
# ==========================================================
import requests

def send_otp_email_async(email, otp):
    threading.Thread(target=send_otp_email, args=(email, otp)).start()

def send_otp_email(receiver_email, otp):
    sender_email = os.environ.get("EMAIL_USER")
    app_password = os.environ.get("EMAIL_PASS")

    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "OTP Verification"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        print("OTP EMAIL SENT SUCCESSFULLY")

    except Exception as e:
        print("Email Error:", e)

# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():
    return render_template("index.html")

# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    stats = get_dashboard_stats() or {}

    return render_template(
        "dashboard.html",
        total_transactions=stats.get("total", 0),
        fraud_count=stats.get("fraud", 0),
        genuine_count=stats.get("genuine", 0),
        detection_rate=stats.get("fraud_rate", 0)
    )

# ==========================================================
# PREDICTION
# ==========================================================

@app.route("/predict", methods=["GET", "POST"])
def predict():

    result = None
    probability = None
    risk_score = None

    if request.method == "POST":

        if (rf_model is None and xgb_model is None) or scaler is None:
            return render_template("predict.html", error="Model not loaded properly")

        try:
            import pandas as pd

            data = pd.DataFrame([{
                "transaction_amount": float(request.form["transaction_amount"]),
                "transaction_type": request.form["transaction_type"],
                "merchant_category": request.form["merchant_category"],
                "transaction_time": request.form["transaction_time"],
                "customer_age": int(request.form["customer_age"]),
                "previous_fraud_history": request.form["previous_fraud_history"],
                "new_device_used": request.form["new_device_used"],
                "international_transaction": request.form["international_transaction"],
                "location_match": request.form["location_match"],
                "transactions_today": int(request.form["transactions_today"])
            }])

            data["risk_score"] = (
                (data["transaction_amount"] > 50000).astype(int) +
                (data["transactions_today"] > 10).astype(int) +
                (data["new_device_used"] == "Yes").astype(int) +
                (data["international_transaction"] == "Yes").astype(int) +
                (data["location_match"] == "No").astype(int) +
                (data["previous_fraud_history"] == "Yes").astype(int)
            )

            risk_score = int(data["risk_score"].iloc[0])

            for col, encoder in encoders.items():
                if col in data.columns:
                    try:
                        data[col] = encoder.transform(data[col])
                    except:
                        data[col] = 0

            data = data.reindex(columns=scaler.feature_names_in_, fill_value=0)

            scaled = scaler.transform(data)

            # use available model (random forest preferred)
            active_model = rf_model if rf_model is not None else xgb_model
            if active_model is None:
                raise Exception("No model available for prediction")

            prediction = active_model.predict(scaled)[0]
            probability = round(active_model.predict_proba(scaled)[0][1] * 100, 2)

            result = "Fraud" if prediction == 1 else "Genuine"

            save_transaction(
                amount=float(request.form["transaction_amount"]),
                transaction_type=request.form["transaction_type"],
                merchant_category=request.form["merchant_category"],
                result=result,
                probability=probability,
                risk_score=risk_score
            )

        except Exception as e:
            print("Prediction Error:", e)
            return render_template("predict.html", error=str(e))

    return render_template(
        "predict.html",
        prediction=result,
        probability=probability,
        risk_score=risk_score
    )

# ==========================================================
# HISTORY (FIXED - SINGLE RETURN ONLY)
# ==========================================================

@app.route("/history")
def history():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    transactions = get_all_transactions()
    return render_template("history.html", transactions=transactions)

# ==========================================================
# LOGIN / REGISTER / OTP (UNCHANGED)
# ==========================================================


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:

            otp = str(random.randint(100000, 999999))

            session["otp"] = otp
            session["username"] = username
            session["temp_email"] = user[2]
            send_otp_email_async(user[2], otp)

            return redirect(url_for("verify_otp"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))

        except:
            return render_template("register.html", error="User already exists")

    return render_template("register.html")


@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        if request.form["otp"] == session.get("otp"):
            session["logged_in"] = True
            return redirect(url_for("dashboard"))

        return render_template("verify_otp.html", error="Invalid OTP")

    return render_template("verify_otp.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)