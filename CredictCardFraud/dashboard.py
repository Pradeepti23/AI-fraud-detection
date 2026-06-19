# ==========================================================
# DASHBOARD.PY - BUSINESS LOGIC LAYER
# CREDIT CARD FRAUD DETECTION SYSTEM
# ==========================================================

from database import (
    get_dashboard_stats,
    get_recent_transactions,
    get_all_transactions
)

# ==========================================================
# GET MAIN DASHBOARD DATA
# ==========================================================
def load_dashboard_data():

    stats = get_dashboard_stats()
    recent_transactions = get_all_transactions(limit=10)

    return {
        "total_transactions": stats["total"],
        "fraud_count": stats["fraud"],
        "genuine_count": stats["genuine"],
        "fraud_rate": stats["fraud_rate"],
        "recent_transactions": recent_transactions
    }

# ==========================================================
# GET FULL REPORT DATA (FOR ANALYTICS PAGE)
# ==========================================================
def load_report_data():

    transactions = get_all_transactions()
    stats = get_dashboard_stats()

    return {
        "stats": stats,
        "transactions": transactions
    }

# ==========================================================
# FRAUD INSIGHTS (OPTIONAL FEATURE FOR MCA PROJECT)
# ==========================================================
def fraud_insights():

    stats = get_dashboard_stats()

    risk_level = "Low"

    if stats["fraud_rate"] > 30:
        risk_level = "High"
    elif stats["fraud_rate"] > 10:
        risk_level = "Medium"

    return {
        "fraud_rate": stats["fraud_rate"],
        "risk_level": risk_level,
        "total_transactions": stats["total"]
    }