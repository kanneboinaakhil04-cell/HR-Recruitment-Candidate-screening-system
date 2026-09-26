document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alert notifications after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Theme Switcher Initialization
    initThemeToggle();
});

function initThemeToggle() {
    const toggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    if (!toggleBtn || !themeIcon) return;

    let currentTheme = document.documentElement.getAttribute('data-theme') || localStorage.getItem('app-theme') || 'dark';

    function updateThemeUI(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('app-theme', theme);
        if (theme === 'light') {
            themeIcon.className = 'fa-solid fa-sun';
            toggleBtn.setAttribute('title', 'Switch to Dark Mode');
        } else {
            themeIcon.className = 'fa-solid fa-moon';
            toggleBtn.setAttribute('title', 'Switch to Light Mode');
        }
    }

    // Apply current theme on init
    updateThemeUI(currentTheme);

    toggleBtn.addEventListener('click', () => {
        currentTheme = (document.documentElement.getAttribute('data-theme') === 'light') ? 'dark' : 'light';
        updateThemeUI(currentTheme);
    });
}

// Update Application Status via AJAX
function updateAppStatus(appId, newStatus) {
    fetch(`/hr/applications/${appId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `status=${encodeURIComponent(newStatus)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const badge = document.getElementById(`status-badge-${appId}`);
            if (badge) {
                badge.textContent = newStatus;
                badge.className = 'badge ' + getBadgeClass(newStatus);
            }
            showToast(`Candidate application status updated to ${newStatus}`);
        } else {
            alert('Failed to update status.');
        }
    })
    .catch(err => console.error('Error:', err));
}

// Update Registered Candidate Direct Status via AJAX
function updateCandidateDirectStatus(candId, newStatus) {
    fetch(`/hr/candidates/${candId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `status=${encodeURIComponent(newStatus)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const badge = document.getElementById(`cand-status-badge-${candId}`);
            if (badge) {
                badge.textContent = newStatus;
                badge.className = 'badge ' + getBadgeClass(newStatus);
            }
            showToast(`Candidate status updated to ${newStatus}`);
        } else {
            alert('Failed to update candidate status.');
        }
    })
    .catch(err => console.error('Error:', err));
}

function getBadgeClass(status) {
    switch (status) {
        case 'Shortlisted': return 'badge-success';
        case 'Reviewing': return 'badge-info';
        case 'Applied': return 'badge-warning';
        case 'Rejected': return 'badge-danger';
        default: return 'badge-info';
    }
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'alert alert-info';
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
