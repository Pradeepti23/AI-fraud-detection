# ==========================================================
# CREDIT CARD FRAUD DETECTION SYSTEM (REFRESHED)
# Random Forest + XGBoost (Improved Version)
# ==========================================================

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)

# ==========================================================
# CREATE MODEL DIRECTORY
# ==========================================================
os.makedirs("model", exist_ok=True)

# ==========================================================
# LOAD DATA
# ==========================================================
df = pd.read_csv(r"C:\Users\HP\Downloads\credit_card_fraud_dataset_10000.csv")

df.drop_duplicates(inplace=True)
df.dropna(inplace=True)

# ==========================================================
# FEATURE ENGINEERING
# ==========================================================
df["amount_category"] = pd.cut(
    df["transaction_amount"],
    bins=[0, 1000, 10000, 50000, 100000],
    labels=["Low", "Medium", "High", "Very_High"]
)

df["high_amount_flag"] = (df["transaction_amount"] > 50000).astype(int)
df["high_frequency_flag"] = (df["transactions_today"] > 10).astype(int)
df["new_device_risk"] = (df["new_device_used"] == "Yes").astype(int)
df["international_risk"] = (df["international_transaction"] == "Yes").astype(int)
df["location_risk"] = (df["location_match"] == "No").astype(int)
df["history_risk"] = (df["previous_fraud_history"] == "Yes").astype(int)

df["risk_score"] = (
    df["high_amount_flag"]
    + df["high_frequency_flag"]
    + df["new_device_risk"]
    + df["international_risk"]
    + df["location_risk"]
    + df["history_risk"]
)

# ==========================================================
# ENCODING
# ==========================================================
categorical_columns = [
    "transaction_type",
    "merchant_category",
    "transaction_time",
    "previous_fraud_history",
    "new_device_used",
    "international_transaction",
    "location_match",
    "amount_category"
]

encoders = {}

for col in categorical_columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

joblib.dump(encoders, "model/label_encoders.pkl")

# ==========================================================
# FEATURES / TARGET
# ==========================================================
X = df.drop("fraud_label", axis=1)
y = df["fraud_label"]

# ==========================================================
# TRAIN TEST SPLIT (IMPORTANT FIX)
# ==========================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ==========================================================
# SCALING (FIT ONLY ON TRAIN)
# ==========================================================
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, "model/scaler.pkl")

# ==========================================================
# RANDOM FOREST
# ==========================================================
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    random_state=42
)

rf.fit(X_train_scaled, y_train)

rf_pred = rf.predict(X_test_scaled)
rf_proba = rf.predict_proba(X_test_scaled)[:, 1]

# ==========================================================
# XGBOOST
# ==========================================================
xgb = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=8,
    eval_metric="logloss",
    random_state=42
)

xgb.fit(X_train_scaled, y_train)

xgb_pred = xgb.predict(X_test_scaled)
xgb_proba = xgb.predict_proba(X_test_scaled)[:, 1]

# ==========================================================
# EVALUATION FUNCTION
# ==========================================================
def evaluate(name, y_test, pred, proba):
    print(f"\n{name}")
    print("Accuracy:", accuracy_score(y_test, pred))
    print("ROC AUC:", roc_auc_score(y_test, proba))
    print(confusion_matrix(y_test, pred))
    print(classification_report(y_test, pred))

# ==========================================================
# RESULTS
# ==========================================================
evaluate("RANDOM FOREST", y_test, rf_pred, rf_proba)
evaluate("XGBOOST", y_test, xgb_pred, xgb_proba)

joblib.dump(rf, "model/random_forest.pkl")
joblib.dump(xgb, "model/xgboost.pkl")

print("\nTraining Completed Successfully")