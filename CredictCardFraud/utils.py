import random

def generate_credit_profile():
    credit_score = random.randint(300, 850)

    if credit_score > 750:
        default_risk = 0.1
    elif credit_score > 600:
        default_risk = 0.3
    else:
        default_risk = 0.7

    credit_limit = credit_score * 2  # simple business rule

    return credit_score, credit_limit, default_risk


def is_defaulter(default_risk, credit_score):
    if default_risk > 0.6 or credit_score < 500:
        return 1
    return 0