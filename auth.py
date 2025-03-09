import time
import uuid
import os

class SimpleAuthManager:
    def __init__(self):
        # Default admin user (for simplicity)
        self.users = {
            'admin': {'password': 'admin', 'role': 'admin', 'created_at': time.time()}
        }
        
        # In-memory sessions
        self.sessions = {}
        
        # Session expiry in seconds (24 hours)
        self.session_expiry = 24 * 60 * 60
    
    def authenticate(self, username, password, session):
        """Authenticate a user and create a session"""
        if username in self.users and self.users[username]['password'] == password:
            # Create session
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                'username': username,
                'created_at': time.time(),
                'last_access': time.time()
            }
            
            # Update session cookie
            session['logged_in'] = True
            session['username'] = username
            session['session_id'] = session_id
            
            return True
        return False
    
    def is_authenticated(self, session):
        """Check if the current session is authenticated"""
        session_id = session.get('session_id')
        if not session_id or session_id not in self.sessions:
            return False
        
        # Check if session has expired
        if time.time() - self.sessions[session_id]['last_access'] > self.session_expiry:
            self.logout(session)
            return False
        
        # Update last access time
        self.sessions[session_id]['last_access'] = time.time()
        return True
    
    def logout(self, session):
        """Logout user and invalidate session"""
        session_id = session.get('session_id')
        if session_id and session_id in self.sessions:
            del self.sessions[session_id]
        
        # Clear session data
        session.clear()
    
    def add_user(self, username, password, role='user'):
        """Add a new user"""
        if username in self.users:
            return False
        
        self.users[username] = {
            'password': password,
            'role': role,
            'created_at': time.time()
        }
        return True
    
    def get_users(self):
        """Get all users (without password)"""
        result = {}
        for username, data in self.users.items():
            result[username] = {
                'role': data['role'],
                'created_at': data['created_at']
            }
        return result
