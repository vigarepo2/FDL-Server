# Templates file containing HTML, CSS, and JavaScript

def render_template_string(template_name):
    """Render a template based on the name"""
    templates = {
        'base': BASE_TEMPLATE,
        'index': INDEX_TEMPLATE,
        'login': LOGIN_TEMPLATE,
        'register': REGISTER_TEMPLATE,
    }
    
    if template_name in templates:
        return templates[template_name]
    else:
        return f"Template '{template_name}' not found."

def get_css():
    """Return the CSS content"""
    return CSS_CONTENT

def get_js():
    """Return the JavaScript content"""
    return JS_CONTENT

# Base template
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FDL Server</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body data-bs-theme="dark">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">FDL Server</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">
                            <i class="bi bi-cloud-download"></i> Downloads
                        </a>
                    </li>
                </ul>
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <button class="btn btn-outline-light btn-sm me-2" id="theme-toggle">
                            <i class="bi bi-moon"></i>
                        </button>
                    </li>
                    {% if current_user.is_authenticated %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="bi bi-person-circle"></i> {{ current_user.username }}
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li><a class="dropdown-item" href="/logout">Logout</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="/login">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/register">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="toast-container position-fixed top-0 end-0 p-3" id="toast-container"></div>

    <div class="container-fluid mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Content will go here -->
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="/static/js/main.js"></script>
</body>
</html>
"""

# Main index template
INDEX_TEMPLATE = """
{% extends "base" %}

{% block content %}
<div class="row">
    <!-- System Dashboard -->
    <div class="col-md-4">
        <div class="card mb-4 shadow-sm">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-speedometer2"></i> System Dashboard
                </h5>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col">
                        <h6>CPU Usage</h6>
                        <div class="progress">
                            <div id="cpu-progress" class="progress-bar" role="progressbar" style="width: 0%"></div>
                        </div>
                        <small id="cpu-text">0% (0 cores)</small>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col">
                        <h6>Memory Usage</h6>
                        <div class="progress">
                            <div id="memory-progress" class="progress-bar" role="progressbar" style="width: 0%"></div>
                        </div>
                        <small id="memory-text">0% (0 GB / 0 GB)</small>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col">
                        <h6>Disk Usage</h6>
                        <div class="progress">
                            <div id="disk-progress" class="progress-bar" role="progressbar" style="width: 0%"></div>
                        </div>
                        <small id="disk-text">0% (0 GB / 0 GB)</small>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col">
                        <canvas id="network-chart" height="100"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Download Form -->
        <div class="card mb-4 shadow-sm">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-cloud-arrow-down"></i> Add Download
                </h5>
            </div>
            <div class="card-body">
                <form id="download-form">
                    <div class="mb-3">
                        <label for="url" class="form-label">URL</label>
                        <div class="input-group">
                            <input type="text" class="form-control" id="url" placeholder="https://example.com/file.zip" required>
                            <button class="btn btn-outline-secondary" type="button" id="paste-url">
                                <i class="bi bi-clipboard"></i>
                            </button>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="filename" class="form-label">Filename (optional)</label>
                        <input type="text" class="form-control" id="filename" placeholder="Leave blank to use original filename">
                    </div>
                    <div class="mb-3">
                        <label for="priority" class="form-label">Priority</label>
                        <select class="form-select" id="priority">
                            <option value="1">Normal</option>
                            <option value="2">High</option>
                            <option value="0">Low</option>
                        </select>
                    </div>
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-download"></i> Start Download
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Active Downloads -->
    <div class="col-md-8">
        <div class="card mb-4 shadow-sm">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="bi bi-arrow-down-circle"></i> Active Downloads
                </h5>
                <div>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-secondary" id="refresh-downloads">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                            <i class="bi bi-sort-down"></i> Sort
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item sort-option" data-sort="progress" href="#">Progress</a></li>
                            <li><a class="dropdown-item sort-option" data-sort="speed" href="#">Speed</a></li>
                            <li><a class="dropdown-item sort-option" data-sort="name" href="#">Name</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="card-body p-0">
                <div class="list-group list-group-flush" id="active-downloads">
                    <!-- Active downloads will be populated here -->
                    <div class="list-group-item text-center py-4 text-muted">
                        <i class="bi bi-cloud-upload fs-2"></i>
                        <p>No active downloads</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Download History -->
        <div class="card shadow-sm">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="bi bi-clock-history"></i> Download History
                </h5>
                <div class="btn-group">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                        <i class="bi bi-funnel"></i> Filter
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item filter-option" data-filter="all" href="#">All</a></li>
                        <li><a class="dropdown-item filter-option" data-filter="completed" href="#">Completed</a></li>
                        <li><a class="dropdown-item filter-option" data-filter="error" href="#">Failed</a></li>
                    </ul>
                </div>
            </div>
            <div class="card-body p-0">
                <div class="list-group list-group-flush" id="download-history">
                    <!-- Download history will be populated here -->
                    <div class="list-group-item text-center py-4 text-muted">
                        <i class="bi bi-clock-history fs-2"></i>
                        <p>No download history</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    // JavaScript for the downloads page
    document.addEventListener('DOMContentLoaded', function() {
        const downloadForm = document.getElementById('download-form');
        const refreshButton = document.getElementById('refresh-downloads');
        const activeDownloadsList = document.getElementById('active-downloads');
        const downloadHistoryList = document.getElementById('download-history');
        
        // Initialize charts and system monitoring
        initSystemMonitoring();
        
        // Load initial downloads and set up periodic refresh
        fetchDownloadStatus();
        setInterval(fetchDownloadStatus, 2000);
        setInterval(fetchSystemInfo, 5000);
        
        // Set up form submission
        downloadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = document.getElementById('url').value;
            const filename = document.getElementById('filename').value;
            const priority = document.getElementById('priority').value;
            
            startDownload(url, filename, priority);
        });
        
        // Download URL pasting
        document.getElementById('paste-url').addEventListener('click', async function() {
            try {
                const text = await navigator.clipboard.readText();
                document.getElementById('url').value = text;
            } catch (err) {
                showToast('Error accessing clipboard', 'danger');
            }
        });
        
        // Manual refresh button
        refreshButton.addEventListener('click', fetchDownloadStatus);
        
        // Handle drag and drop for file URLs
        setupDragAndDrop();
    });
    
    // Function to start a new download
    function startDownload(url, filename, priority) {
        fetch('/api/downloads', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                filename: filename || null,
                priority: parseInt(priority) || 1
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                showToast('Download started', 'success');
                document.getElementById('url').value = '';
                document.getElementById('filename').value = '';
            } else if (data.status === 'duplicate') {
                showToast('File already exists', 'warning');
            } else {
                showToast('Error starting download', 'danger');
            }
            fetchDownloadStatus();
        })
        .catch(error => {
            showToast('Error: ' + error, 'danger');
        });
    }
    
    // Function to cancel a download
    function cancelDownload(downloadId) {
        fetch(`/api/downloads/${downloadId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'cancelled') {
                showToast('Download cancelled', 'info');
            } else {
                showToast('Error cancelling download', 'danger');
            }
            fetchDownloadStatus();
        })
        .catch(error => {
            showToast('Error: ' + error, 'danger');
        });
    }
    
    // Function to fetch download status
    function fetchDownloadStatus() {
        fetch('/api/downloads/status')
        .then(response => response.json())
        .then(data => {
            updateDownloadsList(data.active, data.history);
        })
        .catch(error => {
            console.error('Error fetching download status:', error);
        });
    }
    
    // Function to update the downloads list UI
    function updateDownloadsList(activeDownloads, downloadHistory) {
        const activeDownloadsList = document.getElementById('active-downloads');
        const downloadHistoryList = document.getElementById('download-history');
        
        // Update active downloads
        if (activeDownloads.length > 0) {
            activeDownloadsList.innerHTML = '';
            
            activeDownloads.forEach(download => {
                const item = document.createElement('div');
                item.className = 'list-group-item';
                
                let statusBadge = '';
                switch (download.status) {
                    case 'downloading':
                        statusBadge = '<span class="badge bg-primary">Downloading</span>';
                        break;
                    case 'paused':
                        statusBadge = '<span class="badge bg-warning">Paused</span>';
                        break;
                    case 'cancelling':
                        statusBadge = '<span class="badge bg-danger">Cancelling</span>';
                        break;
                    default:
                        statusBadge = `<span class="badge bg-secondary">${download.status}</span>`;
                }
                
                item.innerHTML = `
                    <div class="d-flex w-100 justify-content-between align-items-center">
                        <h6 class="mb-1 text-truncate" title="${download.filename}">${download.filename}</h6>
                        ${statusBadge}
                    </div>
                    <div class="progress mb-2" style="height: 10px;">
                        <div class="progress-bar progress-bar-animated progress-bar-striped" 
                             role="progressbar" 
                             style="width: ${download.progress}%">
                        </div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            ${download.progress}% • ${download.speed} • ${download.eta}
                        </small>
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline-danger cancel-download" 
                                    data-id="${download.id}">
                                <i class="bi bi-x-circle"></i> Cancel
                            </button>
                        </div>
                    </div>
                    <small class="text-muted d-block text-truncate" title="${download.url}">
                        <i class="bi bi-link-45deg"></i> ${download.url}
                    </small>
                `;
                
                activeDownloadsList.appendChild(item);
            });
            
            // Add event listeners for cancel buttons
            document.querySelectorAll('.cancel-download').forEach(button => {
                button.addEventListener('click', function() {
                    const downloadId = this.getAttribute('data-id');
                    cancelDownload(downloadId);
                });
            });
        } else {
            activeDownloadsList.innerHTML = `
                <div class="list-group-item text-center py-4 text-muted">
                    <i class="bi bi-cloud-upload fs-2"></i>
                    <p>No active downloads</p>
                </div>
            `;
        }
        
        // Update download history
        if (downloadHistory.length > 0) {
            downloadHistoryList.innerHTML = '';
            
            downloadHistory.forEach(download => {
                const item = document.createElement('div');
                item.className = 'list-group-item';
                
                let statusBadge = '';
                if (download.status === 'completed') {
                    statusBadge = '<span class="badge bg-success">Completed</span>';
                } else if (download.status === 'error') {
                    statusBadge = '<span class="badge bg-danger">Failed</span>';
                } else {
                    statusBadge = `<span class="badge bg-secondary">${download.status}</span>`;
                }
                
                item.innerHTML = `
                    <div class="d-flex w-100 justify-content-between align-items-center">
                        <h6 class="mb-1 text-truncate" title="${download.filename}">${download.filename}</h6>
                        ${statusBadge}
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">${download.size}</small>
                        <small class="text-muted">${download.completed_at}</small>
                    </div>
                `;
                
                downloadHistoryList.appendChild(item);
            });
        } else {
            downloadHistoryList.innerHTML = `
                <div class="list-group-item text-center py-4 text-muted">
                    <i class="bi bi-clock-history fs-2"></i>
                    <p>No download history</p>
                </div>
            `;
        }
    }

    // System monitoring initialization
    function initSystemMonitoring() {
        // Create network chart
        const networkCtx = document.getElementById('network-chart').getContext('2d');
        window.networkChart = new Chart(networkCtx, {
            type: 'line',
            data: {
                labels: Array(10).fill(''),
                datasets: [
                    {
                        label: 'Download',
                        data: Array(10).fill(0),
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Upload',
                        data: Array(10).fill(0),
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Bytes/s'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Network Activity'
                    }
                }
            }
        });
        
        // Initial system info update
        fetchSystemInfo();
    }
    
    // Function to fetch system information
    function fetchSystemInfo() {
        fetch('/api/system/info')
        .then(response => response.json())
        .then(data => {
            updateSystemUI(data);
        })
        .catch(error => {
            console.error('Error fetching system info:', error);
        });
    }
    
    // Function to update the system monitoring UI
    function updateSystemUI(data) {
        // Update CPU
        const cpuProgress = document.getElementById('cpu-progress');
        const cpuText = document.getElementById('cpu-text');
        
        cpuProgress.style.width = `${data.cpu.percent}%`;
        cpuText.textContent = `${data.cpu.percent}% (${data.cpu.cores} cores)`;
        
        // Update Memory
        const memoryProgress = document.getElementById('memory-progress');
        const memoryText = document.getElementById('memory-text');
        
        memoryProgress.style.width = `${data.memory.percent}%`;
        const usedGB = (data.memory.used / (1024 * 1024 * 1024)).toFixed(1);
        const totalGB = (data.memory.total / (1024 * 1024 * 1024)).toFixed(1);
        memoryText.textContent = `${data.memory.percent}% (${usedGB} GB / ${totalGB} GB)`;
        
        // Update Disk
        const diskProgress = document.getElementById('disk-progress');
        const diskText = document.getElementById('disk-text');
        
        diskProgress.style.width = `${data.disk.percent}%`;
        const usedDiskGB = (data.disk.used / (1024 * 1024 * 1024)).toFixed(1);
        const totalDiskGB = (data.disk.total / (1024 * 1024 * 1024)).toFixed(1);
        diskText.textContent = `${data.disk.percent}% (${usedDiskGB} GB / ${totalDiskGB} GB)`;
        
        // Update Network Chart
        updateNetworkChart(data.network.received, data.network.sent);
    }
    
    // Network chart update logic
    let lastRecv = 0;
    let lastSent = 0;
    
    function updateNetworkChart(recv, sent) {
        const chart = window.networkChart;
        
        // Calculate speeds
        let recvSpeed = 0;
        let sentSpeed = 0;
        
        if (lastRecv > 0 && lastSent > 0) {
            recvSpeed = recv - lastRecv;
            sentSpeed = sent - lastSent;
        }
        
        lastRecv = recv;
        lastSent = sent;
        
        // Update chart data
        chart.data.labels.shift();
        chart.data.labels.push('');
        
        chart.data.datasets[0].data.shift();
        chart.data.datasets[0].data.push(recvSpeed);
        
        chart.data.datasets[1].data.shift();
        chart.data.datasets[1].data.push(sentSpeed);
        
        chart.update();
    }
    
    // Toast notification function
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center border-0 bg-${type}`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body text-white">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 3000
        });
        
        toast.show();
        
        // Remove the element after it's hidden
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastContainer.removeChild(toastEl);
        });
    }
    
    // Drag and drop setup
    function setupDragAndDrop() {
        const dropZone = document.getElementById('download-form');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropZone.classList.add('border', 'border-primary', 'bg-light');
        }
        
        function unhighlight() {
            dropZone.classList.remove('border', 'border-primary', 'bg-light');
        }
        
        dropZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const url = dt.getData('text/plain');
            
            if (url) {
                document.getElementById('url').value = url;
                showToast('URL added from drag and drop', 'info');
            }
        }
    }
</script>
{% endblock %}
"""

# Login template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - FDL Server</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body data-bs-theme="dark">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                <div class="text-center mb-4">
                    <i class="bi bi-cloud-download display-1"></i>
                    <h2 class="mt-3">FDL Server</h2>
                    <p class="text-muted">File Download Manager</p>
                </div>
                
                <div class="card shadow-sm">
                    <div class="card-header">
                        <h4 class="mb-0">Login</h4>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                                        {{ message }}
                                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" action="/login">
                            <div class="mb-3">
                                <label for="username" class="form-label">Username</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <div class="mb-3 form-check">
                                <input type="checkbox" class="form-check-input" id="remember_me" name="remember_me">
                                <label class="form-check-label" for="remember_me">Remember me</label>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">
                                    <i class="bi bi-box-arrow-in-right"></i> Login
                                </button>
                            </div>
                        </form>
                    </div>
                    <div class="card-footer text-center">
                        <p class="mb-0">
                            Don't have an account? <a href="/register">Register</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Register template
REGISTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - FDL Server</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body data-bs-theme="dark">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                <div class="text-center mb-4">
                    <i class="bi bi-cloud-download display-1"></i>
                    <h2 class="mt-3">FDL Server</h2>
                    <p class="text-muted">File Download Manager</p>
                </div>
                
                <div class="card shadow-sm">
                    <div class="card-header">
                        <h4 class="mb-0">Create an Account</h4>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                                        {{ message }}
                                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" action="/register">
                            <div class="mb-3">
                                <label for="username" class="form-label">Username</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" name="email" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">
                                    <i class="bi bi-person-plus"></i> Register
                                </button>
                            </div>
                        </form>
                    </div>
                    <div class="card-footer text-center">
                        <p class="mb-0">
                            Already have an account? <a href="/login">Login</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# CSS content
CSS_CONTENT = """
:root {
    --transition-speed: 0.3s;
}

body {
    transition: background-color var(--transition-speed), color var(--transition-speed);
}

.card {
    transition: background-color var(--transition-speed), border-color var(--transition-speed);
}

.navbar {
    transition: background-color var(--transition-speed);
}

/* Progress bar animations */
.progress-bar-animated {
    animation: progress-bar-stripes 1s linear infinite;
}

/* Card hover effects */
.card {
    box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.1);
    transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.2);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .card {
        margin-bottom: 1rem;
    }
    
    .card-header h5 {
        font-size: 1.1rem;
    }
}

/* Drop zone styling */
#download-form.highlight {
    border: 2px dashed #3498db !important;
    background-color: rgba(52, 152, 219, 0.1) !important;
}

/* Toast styling */
.toast {
    opacity: 0.9;
    transition: opacity 0.3s;
}

.toast:hover {
    opacity: 1;
}
"""

# JavaScript content
JS_CONTENT = """
// Theme toggler
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const htmlElement = document.documentElement;
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    
    // Set up theme toggle button
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.body.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });
    
    function setTheme(theme) {
        document.body.setAttribute('data-bs-theme', theme);
        
        if (theme === 'dark') {
            themeToggle.innerHTML = '<i class="bi bi-sun"></i>';
        } else {
            themeToggle.innerHTML = '<i class="bi bi-moon"></i>';
        }
    }
});

// Add system routes for monitoring
document.addEventListener('DOMContentLoaded', function() {
    // Add system monitoring endpoint to Flask routes
    if (typeof fetchSystemInfo === 'undefined') {
        window.fetchSystemInfo = function() {
            // This is a fallback if the specific page doesn't have this function
            console.log('System monitoring not initialized on this page');
        };
    }
});
"""
