import os
import threading
import time
import hashlib
import requests
import psutil
import humanize
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
import aria2p
from templates import render_template_string, get_css, get_js

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DOWNLOAD_DIRECTORY = os.environ.get('DOWNLOAD_DIR') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
    TEMP_DIRECTORY = os.environ.get('TEMP_DIR') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads/temp')
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=14)

# Initialize Flask and extensions
app = Flask(__name__)
app.config.from_object(Config)

# Create directories if they don't exist
os.makedirs(app.config['DOWNLOAD_DIRECTORY'], exist_ok=True)
os.makedirs(app.config['TEMP_DIRECTORY'], exist_ok=True)

# Configure static folder for CSS and JS
@app.route('/static/css/style.css')
def serve_css():
    return get_css(), 200, {'Content-Type': 'text/css'}

@app.route('/static/js/main.js')
def serve_js():
    return get_js(), 200, {'Content-Type': 'application/javascript'}

# Database setup
db = SQLAlchemy(app)

# Login manager setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Security utilities
def validate_url(url):
    """Validate that a URL is safe and properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https', 'ftp']
    except:
        return False

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal and command injection."""
    if not filename:
        return None
        
    # Replace potentially dangerous characters
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # Ensure no path traversal
    sanitized = os.path.basename(sanitized)
    
    return sanitized

# System Monitor
class SystemMonitor:
    @staticmethod
    def get_system_info():
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        
        # Disk usage for the download directory
        disk_info = psutil.disk_usage(os.path.abspath(os.getcwd()))
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'cores': psutil.cpu_count()
            },
            'memory': {
                'total': memory_info.total,
                'available': memory_info.available,
                'used': memory_info.used,
                'percent': memory_info.percent
            },
            'disk': {
                'total': disk_info.total,
                'free': disk_info.free,
                'used': disk_info.used,
                'percent': disk_info.percent
            },
            'network': {
                'sent': psutil.net_io_counters().bytes_sent,
                'received': psutil.net_io_counters().bytes_recv
            },
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }

# Download Manager Class
class DownloadManager:
    def __init__(self, download_dir, temp_dir):
        self.download_dir = download_dir
        self.temp_dir = temp_dir
        self.active_downloads = {}
        self.download_history = {}
        self.aria2_available = self._check_aria2_available()
        
        if self.aria2_available:
            try:
                self.aria2 = aria2p.API(
                    aria2p.Client(
                        host="http://localhost",
                        port=6800,
                        secret=""
                    )
                )
            except Exception:
                self.aria2_available = False
    
    def _check_aria2_available(self):
        # Check if aria2c daemon is running
        try:
            for process in psutil.process_iter(['name']):
                if 'aria2c' in process.info['name']:
                    return True
            return False
        except:
            return False
    
    def start_download(self, url, filename=None, user_id=None, priority=1):
        # Generate a unique download ID
        download_id = hashlib.md5((url + str(time.time())).encode()).hexdigest()
        
        if not filename:
            filename = os.path.basename(urlparse(url).path) or f"download_{download_id[:8]}"
        
        temp_path = os.path.join(self.temp_dir, f"{download_id}_{filename}")
        final_path = os.path.join(self.download_dir, filename)
        
        # Check if file already exists (using MD5)
        if os.path.exists(final_path):
            file_hash = self._calculate_file_hash(final_path)
            for download in self.download_history.values():
                if download.get('hash') == file_hash:
                    return {'status': 'duplicate', 'id': download_id, 'message': 'File already exists'}
        
        download_info = {
            'id': download_id,
            'url': url,
            'filename': filename,
            'temp_path': temp_path,
            'final_path': final_path,
            'start_time': datetime.now(),
            'status': 'starting',
            'progress': 0,
            'speed': 0,
            'eta': None,
            'size': 0,
            'downloaded': 0,
            'user_id': user_id,
            'priority': priority,
            'cancel_flag': threading.Event(),
        }
        
        self.active_downloads[download_id] = download_info
        
        # Start download in a separate thread
        thread = threading.Thread(
            target=self._download_thread,
            args=(download_id, url, temp_path, final_path),
            daemon=True
        )
        thread.start()
        
        return {'status': 'started', 'id': download_id}
    
    def _download_thread(self, download_id, url, temp_path, final_path):
        download_info = self.active_downloads[download_id]
        
        try:
            # Try to get file size
            response = requests.head(url, allow_redirects=True)
            size = int(response.headers.get('content-length', 0))
            download_info['size'] = size
            
            if self.aria2_available and size > 1024 * 1024:  # Use aria2 for files > 1MB
                self._aria2_download(download_id, url, temp_path, final_path)
            else:
                self._requests_download(download_id, url, temp_path, final_path)
        
        except Exception as e:
            download_info['status'] = 'error'
            download_info['error'] = str(e)
            self.download_history[download_id] = download_info.copy()
            self._cleanup_download(download_id)
    
    def _requests_download(self, download_id, url, temp_path, final_path):
        download_info = self.active_downloads[download_id]
        download_info['status'] = 'downloading'
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            download_info['size'] = total_size
            
            start_time = time.time()
            downloaded = 0
            
            with open(temp_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if download_info['cancel_flag'].is_set():
                        download_info['status'] = 'cancelled'
                        self._cleanup_download(download_id)
                        return
                    
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        download_info['downloaded'] = downloaded
                        
                        # Update progress
                        if total_size > 0:
                            download_info['progress'] = (downloaded / total_size) * 100
                        
                        # Update speed and ETA
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            speed = downloaded / elapsed
                            download_info['speed'] = speed
                            
                            if speed > 0 and total_size > 0:
                                eta_seconds = (total_size - downloaded) / speed
                                download_info['eta'] = humanize.naturaldelta(eta_seconds)
            
            # Download completed successfully
            os.rename(temp_path, final_path)
            download_info['status'] = 'completed'
            download_info['progress'] = 100
            download_info['hash'] = self._calculate_file_hash(final_path)
            self.download_history[download_id] = download_info.copy()
            
        except Exception as e:
            download_info['status'] = 'error'
            download_info['error'] = str(e)
            self.download_history[download_id] = download_info.copy()
        
        finally:
            self._cleanup_download(download_id)
    
    def _aria2_download(self, download_id, url, temp_path, final_path):
        download_info = self.active_downloads[download_id]
        download_info['status'] = 'downloading'
        
        try:
            # Add download to aria2
            download = self.aria2.add_uris(
                [url],
                options={
                    "dir": os.path.dirname(temp_path),
                    "out": os.path.basename(temp_path),
                    "max-connection-per-server": "16",
                    "split": "16",
                    "min-split-size": "1M"
                }
            )
            
            gid = download.gid
            
            # Monitor download progress
            while True:
                if download_info['cancel_flag'].is_set():
                    self.aria2.remove([gid])
                    download_info['status'] = 'cancelled'
                    self._cleanup_download(download_id)
                    return
                
                download = self.aria2.get_download(gid)
                
                if download.is_complete:
                    os.rename(temp_path, final_path)
                    download_info['status'] = 'completed'
                    download_info['progress'] = 100
                    download_info['hash'] = self._calculate_file_hash(final_path)
                    self.download_history[download_id] = download_info.copy()
                    break
                
                elif download.has_failed:
                    download_info['status'] = 'error'
                    download_info['error'] = f"Aria2 download failed: {download.error_message}"
                    self.download_history[download_id] = download_info.copy()
                    break
                
                # Update progress information
                total_length = download.total_length
                completed_length = download.completed_length
                
                if total_length > 0:
                    download_info['size'] = total_length
                    download_info['downloaded'] = completed_length
                    download_info['progress'] = (completed_length / total_length) * 100
                    download_info['speed'] = download.download_speed
                    
                    if download.download_speed > 0:
                        eta_seconds = (total_length - completed_length) / download.download_speed
                        download_info['eta'] = humanize.naturaldelta(eta_seconds)
                
                time.sleep(0.5)
        
        except Exception as e:
            download_info['status'] = 'error'
            download_info['error'] = str(e)
            self.download_history[download_id] = download_info.copy()
        
        finally:
            self._cleanup_download(download_id)
    
    def cancel_download(self, download_id):
        if download_id in self.active_downloads:
            # Set the cancel flag
            self.active_downloads[download_id]['cancel_flag'].set()
            self.active_downloads[download_id]['status'] = 'cancelling'
            return True
        return False
    
    def _cleanup_download(self, download_id):
        # Remove from active downloads
        if download_id in self.active_downloads:
            download_info = self.active_downloads[download_id]
            
            # Clean up partial file if it exists
            if os.path.exists(download_info['temp_path']):
                try:
                    os.remove(download_info['temp_path'])
                except:
                    pass
            
            # If this was a cancelled download, remove from history
            if download_info['status'] == 'cancelled':
                if download_id in self.download_history:
                    del self.download_history[download_id]
            
            del self.active_downloads[download_id]
    
    def _calculate_file_hash(self, file_path):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

# Initialize the download manager
download_manager = None

@app.before_first_request
def initialize():
    global download_manager
    
    # Create database tables
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin')  # Change in production!
        db.session.add(admin)
        db.session.commit()
    
    # Initialize download manager
    download_dir = app.config['DOWNLOAD_DIRECTORY']
    temp_dir = app.config['TEMP_DIRECTORY']
    download_manager = DownloadManager(download_dir, temp_dir)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember_me') == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
            
        return redirect(next_page)
        
    return render_template_string('login')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
        
    return render_template_string('register')

# Main routes
@app.route('/')
@login_required
def index():
    return render_template_string('index')

@app.route('/api/downloads', methods=['POST'])
@login_required
def start_download():
    data = request.json
    url = data.get('url')
    filename = data.get('filename')
    priority = int(data.get('priority', 1))
    
    if not url:
        return jsonify({'status': 'error', 'message': 'URL is required'}), 400
    
    # Validate URL
    if not validate_url(url):
        return jsonify({'status': 'error', 'message': 'Invalid URL'}), 400
    
    # Sanitize filename if provided
    if filename:
        filename = sanitize_filename(filename)
    
    # Rate limiting logic for the current user
    user_id = current_user.id
    current_time = time.time()
    
    # Check if user has more than 5 downloads in the last minute
    recent_downloads = [d for d in download_manager.active_downloads.values() 
                       if d['user_id'] == user_id and 
                          d['start_time'] > datetime.now() - timedelta(minutes=1)]
                          
    if len(recent_downloads) >= 5:
        return jsonify({'status': 'error', 'message': 'Rate limit exceeded. Please wait before adding more downloads.'}), 429
    
    result = download_manager.start_download(
        url=url,
        filename=filename,
        user_id=user_id,
        priority=priority
    )
    
    return jsonify(result)

@app.route('/api/downloads/<download_id>', methods=['DELETE'])
@login_required
def cancel_download(download_id):
    result = download_manager.cancel_download(download_id)
    
    if result:
        return jsonify({'status': 'cancelled'})
    
    return jsonify({'status': 'error', 'message': 'Download not found'}), 404

@app.route('/api/downloads/status')
@login_required
def get_download_status():
    # Only return downloads for the current user
    active_downloads = {
        k: v for k, v in download_manager.active_downloads.items()
        if v['user_id'] == current_user.id
    }
    
    download_history = {
        k: v for k, v in download_manager.download_history.items()
        if v['user_id'] == current_user.id
    }
    
    # Format the data for the frontend
    active = [
        {
            'id': info['id'],
            'filename': info['filename'],
            'progress': round(info['progress'], 1),
            'speed': humanize.naturalsize(info['speed']) + '/s' if info['speed'] else 'N/A',
            'eta': info['eta'] or 'Calculating...',
            'size': humanize.naturalsize(info['size']) if info['size'] else 'Unknown',
            'status': info['status'],
            'url': info['url'],
        }
        for info in active_downloads.values()
    ]
    
    history = [
        {
            'id': info['id'],
            'filename': info['filename'],
            'size': humanize.naturalsize(info['size']) if info['size'] else 'Unknown',
            'status': info['status'],
            'url': info['url'],
            'completed_at': info.get('start_time').strftime('%Y-%m-%d %H:%M:%S') if info.get('start_time') else 'N/A',
        }
        for info in download_history.values()
    ]
    
    return jsonify({
        'active': active,
        'history': history
    })

@app.route('/api/system/info')
@login_required
def system_info():
    return jsonify(SystemMonitor.get_system_info())

if __name__ == '__main__':
    app.run(debug=True)
