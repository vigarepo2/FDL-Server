TEMPLATES = {
    'login': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FDL Server - Login</title>
    <style>
        :root {
            --primary-color: #4285f4;
            --primary-dark: #3367d6;
            --background: #f5f5f5;
            --card-bg: #ffffff;
            --text: #333333;
            --border: #dddddd;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: var(--background);
            color: var(--text);
            line-height: 1.6;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        
        .login-container {
            width: 100%;
            max-width: 400px;
            background-color: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 2rem;
        }
        
        .login-header {
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        .login-header h1 {
            color: var(--primary-color);
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border);
            border-radius: 4px;
            font-size: 1rem;
            transition: border 0.2s;
        }
        
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: var(--primary-color);
            outline: none;
            box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.2);
        }
        
        button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 12px 16px;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 1rem;
        }
        
        button:hover {
            background-color: var(--primary-dark);
        }
        
        .alert {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #669df6;
                --primary-dark: #4285f4;
                --background: #121212;
                --card-bg: #1e1e1e;
                --text: #e0e0e0;
                --border: #444444;
            }
            
            .alert {
                background-color: #472b2e;
                color: #f8d7da;
            }
        }

        @media (max-width: 480px) {
            .login-container {
                padding: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>FDL Server</h1>
            <p>Fast Download Server</p>
        </div>
        
        {% if get_flashed_messages() %}
            <div class="alert">
                {{ get_flashed_messages()[0] }}
            </div>
        {% endif %}
        
        <form method="post">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
''',

    'index': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FDL Server - Download Manager</title>
    <style>
        :root {
            --primary-color: #4285f4;
            --primary-dark: #3367d6;
            --secondary-color: #34a853;
            --warning-color: #fbbc05;
            --danger-color: #ea4335;
            --background: #f5f5f5;
            --card-bg: #ffffff;
            --text: #333333;
            --text-secondary: #666666;
            --border: #dddddd;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: var(--background);
            color: var(--text);
            line-height: 1.6;
            padding-bottom: 60px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }

        .header-title h1 {
            font-size: 1.8rem;
            color: var(--primary-color);
        }
        
        .header-actions button {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 0.9rem;
            cursor: pointer;
            padding: 5px 10px;
            border-radius: 4px;
        }
        
        .header-actions button:hover {
            background-color: var(--border);
        }
        
        .card {
            background-color: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .form-group {
            display: flex;
            margin-bottom: 10px;
        }
        
        .form-group input[type="url"] {
            flex: 1;
            padding: 12px 15px;
            border: 1px solid var(--border);
            border-radius: 4px 0 0 4px;
            font-size: 1rem;
        }
        
        .form-group button {
            padding: 12px 24px;
            background-color: var(--primary-color);
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 0 4px 4px 0;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .form-group button:hover {
            background-color: var(--primary-dark);
        }
        
        .section-title {
            margin: 30px 0 15px 0;
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text);
        }
        
        .download-list {
            display: grid;
            gap: 15px;
            grid-template-columns: 1fr;
        }
        
        .download-item {
            background-color: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            padding: 15px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .download-info {
            margin-bottom: 10px;
        }
        
        .download-title {
            font-weight: 600;
            margin-bottom: 5px;
            font-size: 1rem;
            word-break: break-all;
        }
        
        .download-url {
            color: var(--text-secondary);
            font-size: 0.8rem;
            margin-bottom: 10px;
            word-break: break-all;
        }
        
        .download-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }
        
        .download-size {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .download-speed {
            font-weight: bold;
            color: var(--primary-color);
            font-size: 1rem;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }
        
        .download-speed::before {
            content: "↓";
            margin-right: 5px;
            font-size: 1.1rem;
        }
        
        .progress-container {
            height: 8px;
            background-color: var(--border);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-bar {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .status-initializing .progress-bar {
            background-color: var(--warning-color);
            animation: pulse 1.5s infinite;
        }
        
        .status-downloading .progress-bar {
            background-color: var(--primary-color);
        }
        
        .status-completed .progress-bar {
            background-color: var(--secondary-color);
        }
        
        .status-error .progress-bar {
            background-color: var(--danger-color);
        }
        
        .status-cancelled .progress-bar {
            background-color: var(--text-secondary);
            width: 100% !important;
            opacity: 0.5;
        }
        
        .download-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        
        .download-actions button {
            padding: 5px 12px;
            border: none;
            border-radius: 4px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .btn-download {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .btn-cancel {
            background-color: var(--danger-color);
            color: white;
        }
        
        .btn-retry {
            background-color: var(--warning-color);
            color: white;
        }
        
        .empty-message {
            text-align: center;
            color: var(--text-secondary);
            padding: 40px 0;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            margin-top: 10px;
        }
        
        .checkbox-group input {
            margin-right: 8px;
        }
        
        .alert {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            display: none;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }

        @media (min-width: 768px) {
            .download-list {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (min-width: 1024px) {
            .download-list {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #669df6;
                --primary-dark: #4285f4;
                --secondary-color: #56ca70;
                --warning-color: #fdd663;
                --danger-color: #f27b6a;
                --background: #121212;
                --card-bg: #1e1e1e;
                --text: #e0e0e0;
                --text-secondary: #a0a0a0;
                --border: #444444;
            }
            
            .alert {
                background-color: #472b2e;
                color: #f8d7da;
            }
        }

        @media (max-width: 480px) {
            header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            
            .header-actions {
                width: 100%;
                display: flex;
                justify-content: space-between;
            }
            
            .form-group {
                flex-direction: column;
            }
            
            .form-group input[type="url"] {
                border-radius: 4px;
                margin-bottom: 10px;
            }
            
            .form-group button {
                border-radius: 4px;
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-title">
                <h1>FDL Server</h1>
            </div>
            
            <div class="header-actions">
                <button id="clearHistoryBtn">Clear History</button>
                <button id="logoutBtn">Logout</button>
            </div>
        </header>
        
        <div class="alert" id="alertMessage"></div>
        
        <div class="card">
            <form id="downloadForm">
                <div class="form-group">
                    <input type="url" id="downloadUrl" placeholder="Enter a download URL" required>
                    <button type="submit">Download</button>
                </div>
                
                <div class="checkbox-group">
                    <input type="checkbox" id="useAria2" checked>
                    <label for="useAria2">Use Aria2 for faster downloads (recommended)</label>
                </div>
            </form>
        </div>
        
        <h2 class="section-title">Active Downloads</h2>
        <div id="activeDownloads" class="download-list">
            <div class="empty-message">No active downloads</div>
        </div>
        
        <h2 class="section-title">Download History</h2>
        <div id="downloadHistory" class="download-list">
            <div class="empty-message">No download history</div>
        </div>
    </div>
    
    <script>
        // DOM elements
        const downloadForm = document.getElementById('downloadForm');
        const downloadUrl = document.getElementById('downloadUrl');
        const useAria2 = document.getElementById('useAria2');
        const activeDownloads = document.getElementById('activeDownloads');
        const downloadHistory = document.getElementById('downloadHistory');
        const clearHistoryBtn = document.getElementById('clearHistoryBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const alertMessage = document.getElementById('alertMessage');

        // Format bytes to human-readable size
        function formatBytes(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
            
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        }
        
        // Create a download item element
        function createDownloadItem(download) {
            const item = document.createElement('div');
            item.className = `download-item status-${download.status}`;
            item.dataset.id = download.id;
            
            let progressText = '';
            if ((download.status === 'downloading' || download.status === 'initializing') && download.size > 0) {
                progressText = `${formatBytes(download.downloaded)} / ${formatBytes(download.size)}`;
            } else if (download.size > 0) {
                progressText = formatBytes(download.size);
            }
            
            const startTime = new Date(download.start_time * 1000).toLocaleString();
            const endTime = download.end_time ? new Date(download.end_time * 1000).toLocaleString() : '';
            
            let statusText = download.status.charAt(0).toUpperCase() + download.status.slice(1);
            if (download.error) {
                statusText = `Error: ${download.error}`;
            }
            
            // Display download speed for active downloads
            let speedDisplay = '';
            if (download.status === 'downloading' && download.speed) {
                speedDisplay = `<div class="download-speed">${download.speed}</div>`;
            }
            
            let actions = '';
            if (download.status === 'completed') {
                actions = `<button class="btn-download" onclick="window.location.href='/downloads/${encodeURIComponent(download.filename)}'">Download</button>`;
            } else if (download.status === 'downloading' || download.status === 'initializing') {
                actions = `<button class="btn-cancel" onclick="cancelDownload('${download.id}')">Cancel</button>`;
            } else if (download.status === 'error') {
                actions = `<button class="btn-retry" onclick="retryDownload('${download.url}')">Retry</button>`;
            }
            
            item.innerHTML = `
                <div class="download-info">
                    <div class="download-title">${download.filename}</div>
                    <div class="download-url">${download.url}</div>
                    <div class="download-meta">
                        <div class="download-status">${statusText}</div>
                        <div class="download-size">${progressText}</div>
                    </div>
                    ${speedDisplay}
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: ${download.progress}%"></div>
                </div>
                <div class="download-meta">
                    <div class="download-time">Started: ${startTime}</div>
                    ${endTime ? `<div class="download-time">Ended: ${endTime}</div>` : ''}
                </div>
                <div class="download-actions">
                    ${actions}
                </div>
            `;
            
            return item;
        }
        
        // Update download list display
        function updateDownloadList(activeList, historyList) {
            // Clear existing items
            activeDownloads.innerHTML = '';
            downloadHistory.innerHTML = '';
            
            if (activeList.length === 0) {
                activeDownloads.innerHTML = '<div class="empty-message">No active downloads</div>';
            } else {
                activeList.forEach(download => {
                    activeDownloads.appendChild(createDownloadItem(download));
                });
            }
            
            if (historyList.length === 0) {
                downloadHistory.innerHTML = '<div class="empty-message">No download history</div>';
            } else {
                historyList.forEach(download => {
                    downloadHistory.appendChild(createDownloadItem(download));
                });
            }
        }
        
        // Fetch all downloads
        function fetchDownloads() {
            fetch('/api/downloads')
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 401) {
                            // Redirect to login page if unauthorized
                            window.location.href = '/login';
                            throw new Error('Session expired. Please log in again.');
                        }
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    updateDownloadList(data.active, data.history);
                })
                .catch(error => {
                    if (!error.message.includes('Session expired')) {
                        showAlert('Failed to fetch downloads: ' + error.message);
                    }
                });
        }
        
        // Add a new download
        function addDownload(url, useAria2) {
            const formData = new FormData();
            formData.append('url', url);
            formData.append('use_aria2', useAria2);
            
            fetch('/api/download', {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 401) {
                            window.location.href = '/login';
                            throw new Error('Session expired. Please log in again.');
                        }
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        downloadUrl.value = '';
                        fetchDownloads();
                    } else {
                        showAlert(data.error || 'Failed to start download');
                    }
                })
                .catch(error => {
                    if (!error.message.includes('Session expired')) {
                        showAlert('Error adding download: ' + error.message);
                    }
                });
        }
        
        // Cancel a download
        function cancelDownload(id) {
            fetch(`/api/download/${id}/cancel`, {
                method: 'POST'
            })
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 401) {
                            window.location.href = '/login';
                            throw new Error('Session expired. Please log in again.');
                        }
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        fetchDownloads();
                    } else {
                        showAlert('Failed to cancel download');
                    }
                })
                .catch(error => {
                    if (!error.message.includes('Session expired')) {
                        showAlert('Error cancelling download: ' + error.message);
                    }
                });
        }
        
        // Retry a failed download
        function retryDownload(url) {
            addDownload(url, useAria2.checked);
        }
        
        // Clear download history
        function clearHistory() {
            if (!confirm('Are you sure you want to clear download history?')) {
                return;
            }
            
            fetch('/api/downloads/clear_history', {
                method: 'POST'
            })
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 401) {
                            window.location.href = '/login';
                            throw new Error('Session expired. Please log in again.');
                        }
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        fetchDownloads();
                    } else {
                        showAlert('Failed to clear history');
                    }
                })
                .catch(error => {
                    if (!error.message.includes('Session expired')) {
                        showAlert('Error clearing history: ' + error.message);
                    }
                });
        }
        
        // Show alert message
        function showAlert(message) {
            alertMessage.textContent = message;
            alertMessage.style.display = 'block';
            setTimeout(() => {
                alertMessage.style.display = 'none';
            }, 5000);
        }
        
        // Event listeners
        downloadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const url = downloadUrl.value.trim();
            if (url) {
                addDownload(url, useAria2.checked);
            }
        });
        
        clearHistoryBtn.addEventListener('click', clearHistory);
        
        logoutBtn.addEventListener('click', function() {
            window.location.href = '/logout';
        });
        
        // Poll for download updates (more frequently for active downloads)
        function pollDownloads() {
            fetchDownloads();
            setTimeout(pollDownloads, 1500); // Update every 1.5 seconds for smoother UI updates
        }
        
        // Initial load
        fetchDownloads();
        pollDownloads();
    </script>
</body>
</html>
'''
}
