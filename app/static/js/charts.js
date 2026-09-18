// Chart theme colors
const COLORS = {
    teal: 'rgb(20, 184, 166)',
    tealLight: 'rgba(20, 184, 166, 0.2)',
    lavender: 'rgb(167, 139, 250)',
    lavenderLight: 'rgba(167, 139, 250, 0.2)',
    mint: 'rgb(52, 211, 153)',
    mintLight: 'rgba(52, 211, 153, 0.2)',
    orange: 'rgb(251, 146, 60)',
    orangeLight: 'rgba(251, 146, 60, 0.2)',
    coral: 'rgb(251, 113, 133)',
    blue: 'rgb(96, 165, 250)',
    purple: 'rgb(192, 132, 252)',
    gold: 'rgb(250, 204, 21)'
};

// Global chart instances registry to destroy before re-creating
const chartInstances = {};

function registerChart(canvasId, chart) {
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }
    chartInstances[canvasId] = chart;
}

function createWellnessChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, COLORS.tealLight);
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Wellness Score',
                data: data,
                borderColor: COLORS.teal,
                backgroundColor: gradient,
                borderWidth: 3,
                pointBackgroundColor: COLORS.teal,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    titleColor: '#333',
                    bodyColor: '#666',
                    borderColor: COLORS.teal,
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { borderDash: [5, 5], color: '#f3f4f6' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
    registerChart(canvasId, chart);
}

function createMoodChart(canvasId, labels, moodData, energyData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Mood',
                    data: moodData,
                    borderColor: COLORS.mint,
                    backgroundColor: COLORS.mintLight,
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: 'Energy',
                    data: energyData,
                    borderColor: COLORS.orange,
                    backgroundColor: COLORS.orangeLight,
                    borderWidth: 2,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 10, grid: { color: '#f3f4f6' } },
                x: { grid: { display: false } }
            }
        }
    });
    registerChart(canvasId, chart);
}

function createActivityChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Completions',
                data: data,
                backgroundColor: COLORS.teal,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
                x: { grid: { display: false } }
            }
        }
    });
    registerChart(canvasId, chart);
}

function createGameRadarChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Score',
                data: data,
                backgroundColor: COLORS.lavenderLight,
                borderColor: COLORS.lavender,
                pointBackgroundColor: COLORS.lavender,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: '#f3f4f6' },
                    grid: { color: '#f3f4f6' },
                    pointLabels: { font: { size: 11 } }
                }
            }
        }
    });
    registerChart(canvasId, chart);
}

function createEngagementDoughnut(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [COLORS.blue, COLORS.purple, COLORS.coral],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
    registerChart(canvasId, chart);
}

function createCorrelationScatter(canvasId, sleepData, stressData) {
    // We combine sleep and stress to form {x, y} pairs for scatter
    // x = sleep hours, y = stress level
    
    // Prepare proper scatter data format
    const scatterData = [];
    for(let i=0; i<Math.min(sleepData.length, stressData.length); i++) {
        scatterData.push({
            x: sleepData[i].y, // sleep hours
            y: stressData[i].y  // stress level
        });
    }

    const ctx = document.getElementById(canvasId).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Sleep vs Stress',
                data: scatterData,
                backgroundColor: COLORS.coral,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Sleep Hours' },
                    grid: { color: '#f3f4f6' }
                },
                y: {
                    title: { display: true, text: 'Stress Level (1-10)' },
                    beginAtZero: true,
                    max: 10,
                    grid: { color: '#f3f4f6' }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (context) => `Sleep: ${context.raw.x}h, Stress: ${context.raw.y}`
                    }
                }
            }
        }
    });
    registerChart(canvasId, chart);
}
