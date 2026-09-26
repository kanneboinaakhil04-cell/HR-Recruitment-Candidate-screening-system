// HR Dashboard Visual Analytics & Live Candidate Table Filter / ADSA QuickSort
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    initTableFilters();
});

function initCharts() {
    const jobChartCtx = document.getElementById('jobChart');
    const scoreChartCtx = document.getElementById('scoreChart');

    if (jobChartCtx && window.chartDataJobs) {
        new Chart(jobChartCtx, {
            type: 'bar',
            data: {
                labels: window.chartDataJobs.labels,
                datasets: [{
                    label: 'Applicants per Job',
                    data: window.chartDataJobs.data,
                    backgroundColor: 'rgba(99, 102, 241, 0.65)',
                    borderColor: '#6366f1',
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: '#94a3b8' } }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }

    if (scoreChartCtx && window.chartDataScores) {
        new Chart(scoreChartCtx, {
            type: 'doughnut',
            data: {
                labels: ['High Match (>75%)', 'Medium Match (50-75%)', 'Low Match (<50%)'],
                datasets: [{
                    data: window.chartDataScores.data,
                    backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: '#94a3b8' } }
                }
            }
        });
    }
}

function initTableFilters() {
    const searchInput = document.getElementById('candidateSearch');
    const jobFilter = document.getElementById('jobFilter');
    const statusFilter = document.getElementById('statusFilter');
    const minMatchFilter = document.getElementById('minMatchFilter');

    if (!searchInput) return;

    function filterRows() {
        const query = searchInput.value.toLowerCase();
        const selectedJob = jobFilter ? jobFilter.value : 'all';
        const selectedStatus = statusFilter ? statusFilter.value : 'all';
        const minMatch = minMatchFilter ? parseFloat(minMatchFilter.value || 0) : 0;

        const rows = document.querySelectorAll('.candidate-row');
        rows.forEach(row => {
            const name = row.dataset.name.toLowerCase();
            const skills = row.dataset.skills.toLowerCase();
            const job = row.dataset.job;
            const status = row.dataset.status;
            const score = parseFloat(row.dataset.score);

            const matchesQuery = name.includes(query) || skills.includes(query);
            const matchesJob = (selectedJob === 'all' || job === selectedJob);
            const matchesStatus = (selectedStatus === 'all' || status === selectedStatus);
            const matchesScore = score >= minMatch;

            if (matchesQuery && matchesJob && matchesStatus && matchesScore) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    searchInput.addEventListener('keyup', filterRows);
    if (jobFilter) jobFilter.addEventListener('change', filterRows);
    if (statusFilter) statusFilter.addEventListener('change', filterRows);
    if (minMatchFilter) minMatchFilter.addEventListener('input', filterRows);
}
