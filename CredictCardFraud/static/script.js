document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form");
    if (!form) return;

    form.addEventListener("submit", (e) => {

        const amount = document.querySelector("[name='transaction_amount']");
        const age = document.querySelector("[name='customer_age']");
        const transactions = document.querySelector("[name='transactions_today']");
        const button = form.querySelector("button");

        if (!amount || !age || !transactions) {
            console.warn("Form inputs missing");
            return;
        }

        const amountVal = parseFloat(amount.value);
        const ageVal = parseInt(age.value);
        const txnVal = parseInt(transactions.value);

        // ================= VALIDATIONS =================

        if (isNaN(amountVal) || amountVal <= 0) {
            alert("Transaction amount must be greater than zero.");
            e.preventDefault();
            return;
        }

        if (isNaN(ageVal) || ageVal < 18 || ageVal > 100) {
            alert("Customer age must be between 18 and 100.");
            e.preventDefault();
            return;
        }

        if (isNaN(txnVal) || txnVal < 0) {
            alert("Transactions today cannot be negative.");
            e.preventDefault();
            return;
        }

        // ================= LOADING STATE =================

        if (button) {
            button.innerHTML = "Predicting...";
            button.disabled = true;
        }
    });

});