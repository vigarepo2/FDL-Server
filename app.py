from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify, send_from_directory
import os
import json
import time
import uuid
from download_manager import DownloadManager
from templates import TEMPLATES

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'fdl-server-secret-key'
app.config['DOWNLOAD_DIR'] = os.environ.get('DOWNLOAD_DIR') or 'downloads'
app.config['TEMP_DIR'] = os.environ.get('TEMP_DIR') or 'downloads/temp'

# In-memory user storage
USERS = {
    'admin': 'password'  # Default user/pass - change this in production!
}

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
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template_string(TEMPLATES['login'])

@app.route('/logout')
def logout():
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
    
    try:
        download_id = download_manager.add_download(url, use_aria2=use_aria2)
        return jsonify({
            'success': True,
            'download_id': download_id
        })
    except Exception as e:
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
    return jsonify({'success': result})

@app.route('/api/downloads/clear_history', methods=['POST'])
def clear_history():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    result = download_manager.clear_download_history()
    return jsonify({'success': result})

@app.route('/downloads/<filename>')
def download_file(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    download_dir = app.config['DOWNLOAD_DIR']
    return send_from_directory(download_dir, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
