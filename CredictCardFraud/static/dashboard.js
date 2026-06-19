let fraudChartInstance = null;
let barChartInstance = null;

function loadFraudChart(fraud, genuine) {

    const ctx = document.getElementById("fraudChart");
    if (!ctx) return;

    if (fraudChartInstance) fraudChartInstance.destroy();

    fraudChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Fraud", "Genuine"],
            datasets: [{
                data: [fraud, genuine],
                backgroundColor: ["#ff4d4d", "#8b5cf6"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function loadBarChart(fraud, genuine) {

    const ctx = document.getElementById("barChart");
    if (!ctx) return;

    if (barChartInstance) barChartInstance.destroy();

    barChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Fraud", "Genuine"],
            datasets: [{
                data: [fraud, genuine],
                backgroundColor: ["#ff4d4d", "#8b5cf6"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    loadFraudChart(fraud, genuine);
    loadBarChart(fraud, genuine);
});