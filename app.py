import os
import json
import time
import datetime
import threading
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from urllib.parse import urlparse  # Using standard library instead of werkzeug.urls
from download_manager import DownloadManager
from auth import SimpleAuthManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'fdl-server-secret-key'
app.config['DOWNLOAD_DIR'] = os.environ.get('DOWNLOAD_DIR') or 'downloads'
app.config['TEMP_DIR'] = os.environ.get('TEMP_DIR') or 'downloads/temp'

# Ensure download directories exist
os.makedirs(app.config['DOWNLOAD_DIR'], exist_ok=True)
os.makedirs(app.config['TEMP_DIR'], exist_ok=True)

# Initialize managers
download_manager = DownloadManager(app.config['DOWNLOAD_DIR'], app.config['TEMP_DIR'])
auth_manager = SimpleAuthManager()

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

@app.route('/')
def index():
    if not auth_manager.is_authenticated(session):
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if auth_manager.is_authenticated(session):
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        if auth_manager.authenticate(form.username.data, form.password.data, session):
            return redirect(url_for('index'))
        flash('Invalid username or password')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    auth_manager.logout(session)
    return redirect(url_for('login'))

@app.route('/downloads')
def downloads():
    if not auth_manager.is_authenticated(session):
        return redirect(url_for('login'))
    
    active = download_manager.get_all_active_downloads()
    history = download_manager.get_download_history()
    return render_template('downloads.html', active_downloads=active, download_history=history)

@app.route('/api/download', methods=['POST'])
def api_download():
    if not auth_manager.is_authenticated(session):
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    download_id = download_manager.add_download(url, session.get('username'))
    return jsonify({"download_id": download_id, "status": "started"})

@app.route('/api/download/<download_id>/status')
def api_download_status(download_id):
    if not auth_manager.is_authenticated(session):
        return jsonify({"error": "Authentication required"}), 401
    
    status = download_manager.get_download_status(download_id)
    if status:
        return jsonify(status)
    return jsonify({"error": "Download not found"}), 404

@app.route('/api/download/<download_id>/cancel', methods=['POST'])
def api_cancel_download(download_id):
    if not auth_manager.is_authenticated(session):
        return jsonify({"error": "Authentication required"}), 401
    
    result = download_manager.cancel_download(download_id)
    if result:
        return jsonify({"status": "cancelled"})
    return jsonify({"error": "Failed to cancel download"}), 400

@app.route('/api/downloads/active')
def api_active_downloads():
    if not auth_manager.is_authenticated(session):
        return jsonify({"error": "Authentication required"}), 401
    
    downloads = download_manager.get_all_active_downloads()
    return jsonify({"downloads": list(downloads.values())})

@app.route('/api/downloads/history')
def api_download_history():
    if not auth_manager.is_authenticated(session):
        return jsonify({"error": "Authentication required"}), 401
    
    history = download_manager.get_download_history()
    return jsonify({"history": list(history.values())})

@app.route('/download/<download_id>')
def download_file(download_id):
    if not auth_manager.is_authenticated(session):
        return redirect(url_for('login'))
    
    # Check if download exists and is completed
    download = download_manager.get_completed_download(download_id)
    if not download:
        flash('Download not found or not completed')
        return redirect(url_for('downloads'))
    
    directory = os.path.dirname(download['file_path'])
    filename = os.path.basename(download['file_path'])
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/settings')
def settings():
    if not auth_manager.is_authenticated(session):
        return redirect(url_for('login'))
    
    return render_template('settings.html', 
                          download_dir=app.config['DOWNLOAD_DIR'],
                          temp_dir=app.config['TEMP_DIR'])

@app.route('/api/system/stats')
def api_system_stats():
    if not auth_manager.is_authenticated(session):
        return jsonify({"error": "Authentication required"}), 401
    
    stats = {
        "active_downloads": len(download_manager.get_all_active_downloads()),
        "completed_downloads": len([d for d in download_manager.get_download_history().values() if d['status'] == 'completed']),
        "failed_downloads": len([d for d in download_manager.get_download_history().values() if d['status'] == 'failed']),
        "total_downloaded": sum(d.get('bytes_downloaded', 0) for d in download_manager.get_download_history().values()),
        "users_count": len(auth_manager.get_users())
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
