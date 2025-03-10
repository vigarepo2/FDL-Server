import os
import time
import threading
import requests
import subprocess
import shutil
import uuid
import signal
from urllib.parse import urlparse, unquote
import re

class DownloadManager:
    def __init__(self, download_dir, temp_dir):
        self.download_dir = os.path.abspath(download_dir)
        self.temp_dir = os.path.abspath(temp_dir)
        self.active_downloads = {}
        self.download_history = {}
        self.lock = threading.Lock()
        self.processes = {}  # Store subprocess references
        
        # Create directories if they don't exist
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Ensure directories are writable
        try:
            os.system(f'chmod -R 777 {self.download_dir}')
            os.system(f'chmod -R 777 {self.temp_dir}')
        except Exception as e:
            print(f"Failed to set permissions: {str(e)}")

    def get_filename_from_url(self, url):
        """Extract filename from URL or response headers"""
        try:
            # Try to get filename from Content-Disposition header
            response = requests.head(url, allow_redirects=True, timeout=10)
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition:
                filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
                if filename_match:
                    return unquote(filename_match.group(1))
            
            # Try to get filename from URL
            path = urlparse(url).path
            filename = os.path.basename(path)
            if filename:
                return unquote(filename)
            
            # Default filename if all else fails
            content_type = response.headers.get('Content-Type', '').split(';')[0].strip()
            extension = self._get_extension_for_content_type(content_type)
            return f"download_{uuid.uuid4().hex[:8]}{extension}"
        except Exception:
            # If all fails, use a random name
            return f"download_{uuid.uuid4().hex[:8]}"
    
    def _get_extension_for_content_type(self, content_type):
        """Map content types to file extensions"""
        content_type_map = {
            'application/pdf': '.pdf',
            'application/zip': '.zip',
            'application/x-rar-compressed': '.rar',
            'application/x-7z-compressed': '.7z',
            'application/x-tar': '.tar',
            'application/x-gzip': '.gz',
            'application/x-bzip2': '.bz2',
            'application/x-zip-compressed': '.zip',
            'application/octet-stream': '.bin',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'video/mp4': '.mp4',
            'video/x-msvideo': '.avi',
            'video/quicktime': '.mov',
            'audio/mpeg': '.mp3',
            'text/plain': '.txt',
            'text/html': '.html',
            'text/csv': '.csv',
            'application/json': '.json',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx'
        }
        return content_type_map.get(content_type, '')

    def add_download(self, url, use_aria2=True):
        """Add a new download job"""
        with self.lock:
            download_id = str(uuid.uuid4())
            
            # Create a unique temporary directory for this download
            temp_dir = os.path.join(self.temp_dir, f"dl_{download_id}")
            os.makedirs(temp_dir, exist_ok=True)
            os.chmod(temp_dir, 0o777)  # Ensure directory is writable
            
            # Get filename from URL or response headers
            filename = self.get_filename_from_url(url)
            
            # Make the filename safe for the filesystem
            filename = self._sanitize_filename(filename)
            
            if not filename:
                filename = f"download_{download_id[:8]}"
            
            temp_path = os.path.join(temp_dir, filename)
            final_path = os.path.join(self.download_dir, filename)
            
            # Create a download job
            download_job = {
                'id': download_id,
                'url': url,
                'filename': filename,
                'start_time': time.time(),
                'end_time': None,
                'temp_path': temp_path,
                'final_path': final_path,
                'progress': 0,
                'status': 'initializing',
                'error': None,
                'size': 0,
                'downloaded': 0,
                'speed': '0 B/s',  # Add speed field
                'temp_dir': temp_dir
            }
            
            self.active_downloads[download_id] = download_job
            
            # Start download in a separate thread
            if use_aria2:
                thread = threading.Thread(target=self._download_with_aria2, args=(download_id, url, temp_dir, temp_path, final_path))
            else:
                thread = threading.Thread(target=self._download_with_requests, args=(download_id, url, temp_path, final_path))
            thread.daemon = True
            thread.start()
            
            return download_id

    def _sanitize_filename(self, filename):
        """Make filename safe for the filesystem"""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Remove control characters
        filename = ''.join(c for c in filename if ord(c) >= 32)
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        return filename or "download"

    def _download_with_aria2(self, download_id, url, temp_dir, temp_path, final_path):
        """Download using aria2c for better performance"""
        try:
            with self.lock:
                if download_id not in self.active_downloads:
                    return
                
                self.active_downloads[download_id]['status'] = 'downloading'
                self.active_downloads[download_id]['speed'] = '0 B/s'  # Initialize speed
            
            # Build aria2c command with enhanced output options
            cmd = [
                'aria2c',
                '--max-connection-per-server=16',
                '--min-split-size=1M',
                '--split=10',
                '--continue=true',
                '--dir', temp_dir,
                '--out', os.path.basename(final_path),
                '--summary-interval=1',  # Update summary every second
                '--console-log-level=notice',  # More verbose output
                '--human-readable=true',  # Human readable output
                '--download-result=full',  # Detailed download result
                url
            ]
            
            # Start aria2c process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None  # For process group control
            )
            
            # Store process reference for potential cancellation
            with self.lock:
                if download_id in self.active_downloads:
                    self.processes[download_id] = process
            
            # Monitor aria2c progress
            total_size = 0
            downloaded = 0
            last_update_time = time.time()
            last_downloaded = 0
            
            while True:
                if download_id in self.active_downloads and self.active_downloads[download_id]['status'] == 'cancelled':
                    # Kill the process if download was cancelled
                    try:
                        if hasattr(os, 'killpg') and hasattr(os, 'getpgid'):
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        else:
                            process.terminate()
                    except Exception:
                        pass
                    return
                
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if not line:
                    continue
                
                # Parse progress information
                try:
                    # Extract percentage
                    percent_match = re.search(r'(\d+)%', line)
                    if percent_match:
                        progress = int(percent_match.group(1))
                        with self.lock:
                            if download_id in self.active_downloads:
                                self.active_downloads[download_id]['progress'] = progress
                    
                    # Extract downloaded/total
                    size_match = re.search(r'\((\d+\.?\d*)([KMGT]?i?B)/(\d+\.?\d*)([KMGT]?i?B)\)', line)
                    if size_match:
                        downloaded_str = size_match.group(1) + size_match.group(2)
                        total_str = size_match.group(3) + size_match.group(4)
                        
                        downloaded = self._parse_size(downloaded_str)
                        total_size = self._parse_size(total_str)
                        
                        with self.lock:
                            if download_id in self.active_downloads:
                                self.active_downloads[download_id]['size'] = total_size
                                self.active_downloads[download_id]['downloaded'] = downloaded
                    
                    # Extract speed information directly from aria2c output
                    speed_match = re.search(r'(\d+\.?\d*[KMGT]?i?B/s)', line)
                    if speed_match:
                        speed = speed_match.group(1)
                        with self.lock:
                            if download_id in self.active_downloads:
                                self.active_downloads[download_id]['speed'] = speed
                    else:
                        # Calculate speed if not provided by aria2c
                        current_time = time.time()
                        elapsed = current_time - last_update_time
                        
                        if elapsed >= 1 and last_downloaded > 0:
                            bytes_per_sec = (downloaded - last_downloaded) / elapsed
                            speed = self._format_speed(bytes_per_sec)
                            
                            with self.lock:
                                if download_id in self.active_downloads:
                                    self.active_downloads[download_id]['speed'] = speed
                            
                            last_update_time = current_time
                            last_downloaded = downloaded
                except Exception as e:
                    print(f"Error parsing aria2c output: {e}")
            
            # Check if download was successful
            if process.returncode == 0:
                # Move file from temp to final location
                temp_file = os.path.join(temp_dir, os.path.basename(final_path))
                if os.path.exists(temp_file):
                    os.makedirs(os.path.dirname(final_path), exist_ok=True)
                    shutil.move(temp_file, final_path)
                    os.chmod(final_path, 0o644)  # Set read permissions for everyone
                    
                    with self.lock:
                        if download_id in self.active_downloads:
                            self.active_downloads[download_id]['status'] = 'completed'
                            self.active_downloads[download_id]['progress'] = 100
                            self.active_downloads[download_id]['end_time'] = time.time()
                            self.active_downloads[download_id]['speed'] = '0 B/s'
                            
                            # Add to download history
                            self.download_history[download_id] = self.active_downloads[download_id].copy()
                else:
                    raise Exception("Download file not found in temp directory")
            else:
                raise Exception(f"aria2c failed with exit code {process.returncode}")
                
        except Exception as e:
            with self.lock:
                if download_id in self.active_downloads:
                    self.active_downloads[download_id]['status'] = 'error'
                    self.active_downloads[download_id]['error'] = str(e)
                    self.active_downloads[download_id]['speed'] = '0 B/s'
            print(f"Download error: {e}")
        finally:
            # Remove from processes
            with self.lock:
                if download_id in self.processes:
                    del self.processes[download_id]
            
            # Clean up temp directory
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass

    def _parse_size(self, size_str):
        """Parse size string like 10.5MB to bytes"""
        units = {'B': 1, 'K': 1024, 'M': 1024*1024, 'G': 1024*1024*1024, 'T': 1024*1024*1024*1024}
        match = re.match(r'^(\d+\.?\d*)([KMGT]?i?B)$', size_str)
        if match:
            size, unit = match.groups()
            unit_char = unit[0].upper() if unit else 'B'
            return int(float(size) * units.get(unit_char, 1))
        return 0

    def _format_speed(self, bytes_per_sec):
        """Format bytes per second to human-readable speed"""
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.1f} B/s"
        elif bytes_per_sec < 1024*1024:
            return f"{bytes_per_sec/1024:.1f} KB/s"
        elif bytes_per_sec < 1024*1024*1024:
            return f"{bytes_per_sec/(1024*1024):.1f} MB/s"
        else:
            return f"{bytes_per_sec/(1024*1024*1024):.1f} GB/s"

    def _download_with_requests(self, download_id, url, temp_path, final_path):
        """Download using requests as a fallback"""
        try:
            with self.lock:
                if download_id not in self.active_downloads:
                    return
                
                self.active_downloads[download_id]['status'] = 'downloading'
                self.active_downloads[download_id]['speed'] = '0 B/s'  # Initialize speed
            
            # Create directory for temp path
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            # Start the download
            session = requests.Session()
            response = session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            with self.lock:
                if download_id in self.active_downloads:
                    self.active_downloads[download_id]['size'] = total_size
            
            # Download the file
            downloaded = 0
            last_update_time = time.time()
            last_downloaded = 0
            chunk_size = 8192
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    # Check if download was cancelled
                    with self.lock:
                        if download_id not in self.active_downloads or self.active_downloads[download_id]['status'] == 'cancelled':
                            return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress
                        current_time = time.time()
                        elapsed = current_time - last_update_time
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            
                            with self.lock:
                                if download_id in self.active_downloads:
                                    self.active_downloads[download_id]['progress'] = progress
                                    self.active_downloads[download_id]['downloaded'] = downloaded
                                    
                                    # Calculate and update speed
                                    if elapsed >= 1:
                                        bytes_per_sec = (downloaded - last_downloaded) / elapsed
                                        speed = self._format_speed(bytes_per_sec)
                                        self.active_downloads[download_id]['speed'] = speed
                                        
                                        last_update_time = current_time
                                        last_downloaded = downloaded
            
            # Move to final location
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            shutil.move(temp_path, final_path)
            os.chmod(final_path, 0o644)  # Set read permissions
            
            with self.lock:
                if download_id in self.active_downloads:
                    self.active_downloads[download_id]['status'] = 'completed'
                    self.active_downloads[download_id]['progress'] = 100
                    self.active_downloads[download_id]['end_time'] = time.time()
                    self.active_downloads[download_id]['speed'] = '0 B/s'
                    
                    # Add to download history
                    self.download_history[download_id] = self.active_downloads[download_id].copy()
            
        except Exception as e:
            with self.lock:
                if download_id in self.active_downloads:
                    self.active_downloads[download_id]['status'] = 'error'
                    self.active_downloads[download_id]['error'] = str(e)
                    self.active_downloads[download_id]['speed'] = '0 B/s'
            print(f"Download error: {e}")
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def get_download_status(self, download_id):
        """Get current status of a download"""
        with self.lock:
            if download_id in self.active_downloads:
                return self.active_downloads[download_id]
            elif download_id in self.download_history:
                return self.download_history[download_id]
            return None

    def get_all_downloads(self):
        """Get all active and completed downloads"""
        with self.lock:
            # Sort downloads by start time (newest first)
            active = sorted(
                list(self.active_downloads.values()), 
                key=lambda x: x['start_time'], 
                reverse=True
            )
            
            history = sorted(
                list(self.download_history.values()), 
                key=lambda x: x['start_time'], 
                reverse=True
            )
            
            return {
                'active': active,
                'history': history
            }

    def cancel_download(self, download_id):
        """Cancel an active download"""
        with self.lock:
            if download_id in self.active_downloads:
                self.active_downloads[download_id]['status'] = 'cancelled'
                
                # Kill associated process if it exists
                if download_id in self.processes:
                    try:
                        process = self.processes[download_id]
                        # Try process group kill first (Linux)
                        try:
                            if hasattr(os, 'killpg') and hasattr(os, 'getpgid'):
                                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                            else:
                                process.terminate()
                        except Exception:
                            process.terminate()
                    except Exception as e:
                        print(f"Failed to terminate process: {e}")
                
                return True
            return False

    def clear_download_history(self):
        """Clear download history"""
        with self.lock:
            self.download_history.clear()
            return True
