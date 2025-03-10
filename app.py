from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify, send_from_directory
import os
import json
import time
import uuid
import logging
from urllib.parse import urlparse  # Using Python's built-in URL parser instead of werkzeug
from download_manager import DownloadManager
from templates import TEMPLATES

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fdl_server')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'fdl-server-secret-key'
app.config['DOWNLOAD_DIR'] = os.environ.get('DOWNLOAD_DIR') or 'downloads'
app.config['TEMP_DIR'] = os.environ.get('TEMP_DIR') or 'downloads/temp'

# In-memory user storage
USERS = {
    'admin': 'password'  # Default user/pass - change this in production!
}

# Ensure directories exist with proper permissions
for directory in [app.config['DOWNLOAD_DIR'], app.config['TEMP_DIR']]:
    os.makedirs(directory, exist_ok=True)
    try:
        # Set full permissions for container environment
        os.system(f'chmod -R 777 {directory}')
    except Exception as e:
        logger.error(f"Failed to set permissions on {directory}: {str(e)}")

# Create download manager
download_manager = DownloadManager(
    download_dir=app.config['DOWNLOAD_DIR'],
    temp_dir=app.config['TEMP_DIR']
)

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(TEMPLATES['index'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            logger.info(f"User '{username}' logged in successfully")
            return redirect(url_for('index'))
        else:
            logger.warning(f"Failed login attempt for user '{username}'")
            flash('Invalid username or password')
    
    return render_template_string(TEMPLATES['login'])

@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    logger.info(f"User '{username}' logged out")
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/download', methods=['POST'])
def add_download():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    url = request.form.get('url')
    use_aria2 = request.form.get('use_aria2', 'true').lower() == 'true'
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Validate URL
    try:
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError("Invalid URL format")
    except Exception:
        logger.warning(f"Invalid URL attempted: {url}")
        return jsonify({'error': 'Invalid URL format'}), 400
    
    try:
        download_id = download_manager.add_download(url, use_aria2=use_aria2)
        logger.info(f"Download added: {url} (ID: {download_id})")
        return jsonify({
            'success': True,
            'download_id': download_id
        })
    except Exception as e:
        logger.error(f"Error adding download {url}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/downloads')
def get_downloads():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    downloads = download_manager.get_all_downloads()
    return jsonify(downloads)

@app.route('/api/download/<download_id>')
def get_download(download_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    download = download_manager.get_download_status(download_id)
    if download:
        return jsonify(download)
    return jsonify({'error': 'Download not found'}), 404

@app.route('/api/download/<download_id>/cancel', methods=['POST'])
def cancel_download(download_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    result = download_manager.cancel_download(download_id)
    logger.info(f"Download cancelled: {download_id}, result: {result}")
    return jsonify({'success': result})

@app.route('/api/downloads/clear_history', methods=['POST'])
def clear_history():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    result = download_manager.clear_download_history()
    logger.info(f"Download history cleared by {session.get('username', 'Unknown')}")
    return jsonify({'success': result})

@app.route('/downloads/<path:filename>')
def download_file(filename):
    # No login check here - files are publicly downloadable
    
    # Secure against path traversal attacks
    if '..' in filename or filename.startswith('/'):
        logger.warning(f"Possible path traversal attempt: {filename}")
        return "Invalid filename", 400
        
    download_dir = app.config['DOWNLOAD_DIR']
    logger.info(f"File download requested: {filename}")
    
    # Check if file exists
    file_path = os.path.join(download_dir, filename)
    if not os.path.isfile(file_path):
        logger.warning(f"File not found: {filename}")
        return "File not found", 404
    
    # Log the download
    user = session.get('username', 'Anonymous')
    ip = request.remote_addr
    logger.info(f"File download: {filename} by {user} from {ip}")
    
    # Send the file as attachment
    return send_from_directory(download_dir, filename, as_attachment=True)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
