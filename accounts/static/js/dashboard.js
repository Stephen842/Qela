document.addEventListener('DOMContentLoaded', () => {
    const chartEl = document.getElementById('mainGrowthChart');
    const labels = JSON.parse(chartEl.dataset.labels.replace(/'/g, '"'));
    const values = JSON.parse(chartEl.dataset.values);

    const ctx = chartEl.getContext('2d');
    
    // Create the soft blue gradient fill seen in the image
    const fillGradient = ctx.createLinearGradient(0, 0, 0, 400);
    fillGradient.addColorStop(0, 'rgba(59, 130, 246, 0.15)');
    fillGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                borderColor: '#3B82F6', // The vibrant blue line
                borderWidth: 3,
                tension: 0.45, // This creates the "wave" look from the image
                pointRadius: 0, // Hides points by default
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#3B82F6',
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 3,
                fill: true,
                backgroundColor: fillGradient,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1e293b', // Dark tooltip like the image
                    titleFont: { size: 13 },
                    bodyFont: { size: 13, weight: 'bold' },
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: (context) => `${context.parsed.y.toLocaleString()} users`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    border: { display: false },
                    grid: { color: '#f1f5f9' },
                    ticks: {
                        color: '#94a3b8',
                        font: { size: 11 },
                        callback: (value) => value >= 1000 ? (value/1000) + 'k' : value
                    }
                },
                x: {
                    border: { display: false },
                    grid: { display: false },
                    ticks: {
                        color: '#94a3b8',
                        font: { size: 11, weight: '500' }
                    }
                }
            }
        }
    });
});