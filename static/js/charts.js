// Chart.js Configuration and Init
document.addEventListener('DOMContentLoaded', async () => {
    const ctx = document.getElementById('viewsChart');
    if (!ctx) return;

    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Sahifa korishlar',
                    data: data.views,
                    borderColor: '#6366f1', // Primary color
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Tashrif buyuruvchilar',
                    data: data.visitors,
                    borderColor: '#ec4899', // Secondary color
                    backgroundColor: 'rgba(236, 72, 153, 0.1)',
                    tension: 0.4,
                    fill: true,
                    hidden: true // Hide by default to keep it clean
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Oxirgi 7 kunlik statistika'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Update summary cards if they exist
        const totalViewsEl = document.getElementById('total-views');
        if (totalViewsEl) totalViewsEl.textContent = data.total_views;

    } catch (error) {
        console.error('Error loading charts:', error);
    }
});
