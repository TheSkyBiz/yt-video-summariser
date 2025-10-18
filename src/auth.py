"""
Authentication and session management
"""
import streamlit as st
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict
from .db_utils import db_manager
from .config import SESSION_TIMEOUT, MIN_PASSWORD_LENGTH
from typing import Optional, Dict, Tuple

class AuthManager:
    def __init__(self):
        self.session_key = "user_session"
    
    def initialize_session_state(self):
        """Initialize authentication-related session state"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        if 'session_id' not in st.session_state:
            st.session_state.session_id = None
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    def login_user(self, username: str, password: str) -> tuple[bool, str]:
        """Authenticate user and create session"""
        user_data = db_manager.authenticate_user(username, password)
        
        if user_data:
            # Create session
            session_id = str(uuid.uuid4())
            st.session_state.authenticated = True
            st.session_state.user_data = user_data
            st.session_state.session_id = session_id
            
            return True, "Login successful"
        else:
            return False, "Invalid username or password"
    
    def register_user(self, username: str, password: str, email: Optional[str] = None) -> Tuple[bool, str]:
        """Register new user"""
        # Validate inputs
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if not username.isalnum():
            return False, "Username can only contain letters and numbers"
        
        password_valid, password_msg = self.validate_password(password)
        if not password_valid:
            return False, password_msg
        
        # Attempt to create user
        success = db_manager.create_user(username, password, email)
        
        if success:
            return True, "Account created successfully"
        else:
            return False, "Username already exists"
    
    def logout_user(self):
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user_data = None
        st.session_state.session_id = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def get_user_data(self) -> Optional[Dict]:
        """Get current user data"""
        return st.session_state.get('user_data')
    
    def require_auth(self):
        """Decorator/function to require authentication"""
        if not self.is_authenticated():
            st.error("Please log in to access this feature")
            st.stop()

# Global auth manager instance
auth_manager = AuthManager()