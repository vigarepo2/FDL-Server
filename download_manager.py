import os
import threading
import time
import uuid
import subprocess
import requests
import shutil
import json
from urllib.parse import urlparse
from datetime import datetime

class DownloadManager:
    def __init__(self, download_dir, temp_dir):
        self.download_dir = download_dir
        self.temp_dir = temp_dir
        self.active_downloads = {}
        self.download_history = {}
        self.lock = threading.Lock()
        os.makedirs(download_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
    
    def add_download(self, url, username):
        download_id = str(uuid.uuid4())
        
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = f"download_{download_id}"
        
        temp_path = os.path.join(self.temp_dir, filename)
        final_path = os.path.join(self.download_dir, filename)
        
        download_info = {
            'id': download_id,
            'url': url,
            'filename': filename,
            'temp_path': temp_path,
            'file_path': final_path,
            'status': 'queued',
            'progress': 0,
            'bytes_downloaded': 0,
            'total_bytes': 0,
            'speed': 0,
            'start_time': time.time(),
            'end_time': None,
            'user': username
        }
        
        with self.lock:
            self.active_downloads[download_id] = download_info
            self.download_history[download_id] = download_info.copy()
        
        # Start download in a separate thread
        download_thread = threading.Thread(target=self._download_worker, args=(download_id,))
        download_thread.daemon = True
        download_thread.start()
        
        return download_id
    
    def _download_worker(self, download_id):
        download = self.active_downloads.get(download_id)
        if not download:
            return
        
        try:
            # Update status to downloading
            self._update_download_status(download_id, status='downloading')
            
            # Try to use aria2c for downloading if available
            if self._is_aria2c_available():
                self._download_with_aria2c(download_id)
            else:
                self._download_with_requests(download_id)
                
            # Move file from temp to download directory
            shutil.move(download['temp_path'], download['file_path'])
            
            # Update status to completed
            self._update_download_status(download_id, status='completed', progress=100)
        except Exception as e:
            self._update_download_status(download_id, status='failed', error=str(e))
        finally:
            # Clean up
            with self.lock:
                if download_id in self.active_downloads:
                    del self.active_downloads[download_id]
    
    def _is_aria2c_available(self):
        try:
            subprocess.run(['aria2c', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    
    def _download_with_aria2c(self, download_id):
        download = self.active_downloads.get(download_id)
        if not download:
            return
        
        # Setup progress file
        progress_file = os.path.join(self.temp_dir, f"{download_id}_progress.txt")
        
        # Prepare aria2c command
        cmd = [
            'aria2c', 
            download['url'], 
            f'--dir={self.temp_dir}',
            f'--out={os.path.basename(download["temp_path"])}',
            '--summary-interval=1',
            '--file-allocation=none',
            '--auto-file-renaming=true',
            '--continue=true',
            '--max-connection-per-server=16',
        ]
        
        # Start aria2c process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Monitor progress
        for line in process.stdout:
            if download_id not in self.active_downloads:
                process.terminate()
                break
                
            if '[#' in line:
                # Extract progress information
                parts = line.strip().split()
                for part in parts:
                    if '%' in part:
                        progress = float(part.replace('%', ''))
                        self._update_download_status(download_id, progress=progress)
                    if 'DL:' in part:
                        speed = part.split('DL:')[1]
                        self._update_download_status(download_id, speed=speed)
        
        # Check if process completed successfully
        if process.wait() != 0 and download_id in self.active_downloads:
            raise Exception(f"aria2c download failed with exit code {process.returncode}")
    
    def _download_with_requests(self, download_id):
        download = self.active_downloads.get(download_id)
        if not download:
            return
        
        with requests.get(download['url'], stream=True) as response:
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            if total_size > 0:
                self._update_download_status(download_id, total_bytes=total_size)
            
            downloaded_size = 0
            start_time = time.time()
            last_update_time = start_time
            
            with open(download['temp_path'], 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if download_id not in self.active_downloads:
                        # Download was cancelled
                        break
                    
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        current_time = time.time()
                        if current_time - last_update_time >= 0.5:  # Update every 0.5 seconds
                            # Calculate progress
                            progress = 0
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                            
                            # Calculate speed (bytes per second)
                            elapsed = current_time - start_time
                            speed = downloaded_size / elapsed if elapsed > 0 else 0
                            speed_str = f"{self._format_size(speed)}/s"
                            
                            self._update_download_status(
                                download_id, 
                                progress=progress, 
                                bytes_downloaded=downloaded_size,
                                speed=speed_str
                            )
                            last_update_time = current_time
    
    def _update_download_status(self, download_id, **kwargs):
        with self.lock:
            if download_id in self.active_downloads:
                for key, value in kwargs.items():
                    self.active_downloads[download_id][key] = value
                
                # Update end_time if status is completed or failed
                if kwargs.get('status') in ['completed', 'failed']:
                    self.active_downloads[download_id]['end_time'] = time.time()
                
                # Update history
                self.download_history[download_id] = self.active_downloads[download_id].copy()
    
    def get_download_status(self, download_id):
        with self.lock:
            # First check active downloads
            if download_id in self.active_downloads:
                return self.active_downloads[download_id]
            # Then check history
            if download_id in self.download_history:
                return self.download_history[download_id]
            return None
    
    def cancel_download(self, download_id):
        with self.lock:
            if download_id in self.active_downloads:
                # Mark as cancelled
                self.active_downloads[download_id]['status'] = 'cancelled'
                self.active_downloads[download_id]['end_time'] = time.time()
                
                # Update history
                self.download_history[download_id] = self.active_downloads[download_id].copy()
                
                # Remove from active downloads
                del self.active_downloads[download_id]
                
                # Try to remove temp file if it exists
                temp_path = self.download_history[download_id]['temp_path']
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                
                return True
            return False
    
    def get_all_active_downloads(self):
        with self.lock:
            return self.active_downloads.copy()
    
    def get_download_history(self):
        with self.lock:
            return self.download_history.copy()
    
    def get_completed_download(self, download_id):
        with self.lock:
            if download_id in self.download_history and self.download_history[download_id]['status'] == 'completed':
                return self.download_history[download_id]
            return None
    
    def _format_size(self, size_bytes):
        """Format size in bytes to human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes:.2f}B"
        
        size_kb = size_bytes / 1024
        if size_kb < 1024:
            return f"{size_kb:.2f}KB"
        
        size_mb = size_kb / 1024
        if size_mb < 1024:
            return f"{size_mb:.2f}MB"
        
        size_gb = size_mb / 1024
        return f"{size_gb:.2f}GB"
