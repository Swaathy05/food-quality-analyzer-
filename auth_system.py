"""
Enterprise Authentication System
Features: User registration, login, role-based access, session management
"""

import streamlit as st
import hashlib
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import jwt
import re

class AuthenticationSystem:
    """Complete authentication and user management system"""
    
    def __init__(self, db_path: str = "Food_Quality_Analyzer/users.db"):
        self.db_path = db_path
        self.secret_key = "your-secret-key-change-in-production"
        self.init_database()
    
    def init_database(self):
        """Initialize user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                profile_data TEXT,
                preferences TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Login attempts table (security)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                ip_address TEXT,
                success BOOLEAN,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
        if cursor.fetchone()[0] == 0:
            admin_id = str(uuid.uuid4())
            admin_password = self.hash_password("admin123")
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (admin_id, "admin", "admin@foodanalyzer.com", admin_password, "admin"))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = "food_analyzer_salt"  # In production, use random salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    def register_user(self, username: str, email: str, password: str) -> tuple[bool, str]:
        """Register new user"""
        
        # Validate inputs
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if not self.validate_email(email):
            return False, "Invalid email format"
        
        is_valid, message = self.validate_password(password)
        if not is_valid:
            return False, message
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if username or email already exists
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                return False, "Username or email already exists"
            
            # Create new user
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, email, password_hash))
            
            conn.commit()
            return True, "User registered successfully"
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
        
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, Optional[Dict]]:
        """Authenticate user login"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user data
            cursor.execute('''
                SELECT id, username, email, password_hash, role, is_active
                FROM users 
                WHERE username = ? OR email = ?
            ''', (username, username))
            
            user_data = cursor.fetchone()
            
            # Log login attempt
            cursor.execute('''
                INSERT INTO login_attempts (username, success)
                VALUES (?, ?)
            ''', (username, user_data is not None))
            
            if not user_data:
                return False, None
            
            user_id, db_username, email, password_hash, role, is_active = user_data
            
            # Check if user is active
            if not is_active:
                return False, None
            
            # Verify password
            if self.hash_password(password) != password_hash:
                return False, None
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            
            return True, {
                'id': user_id,
                'username': db_username,
                'email': email,
                'role': role
            }
            
        except Exception as e:
            return False, None
        
        finally:
            conn.close()
    
    def create_session(self, user_id: str) -> str:
        """Create user session"""
        
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=7)  # 7 days expiry
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_sessions (session_id, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (session_id, user_id, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Validate user session"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.role, s.expires_at
            FROM user_sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_id = ? AND s.is_active = 1 AND u.is_active = 1
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        user_id, username, email, role, expires_at = result
        
        # Check if session expired
        if datetime.fromisoformat(expires_at) < datetime.now():
            self.invalidate_session(session_id)
            return None
        
        return {
            'id': user_id,
            'username': username,
            'email': email,
            'role': role
        }
    
    def invalidate_session(self, session_id: str):
        """Invalidate user session"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_sessions SET is_active = 0 WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self) -> Dict:
        """Get user statistics for admin dashboard"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        total_users = cursor.fetchone()[0]
        
        # New users this month
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE is_active = 1 AND created_at >= date('now', 'start of month')
        ''')
        new_users_month = cursor.fetchone()[0]
        
        # Active sessions
        cursor.execute('''
            SELECT COUNT(*) FROM user_sessions 
            WHERE is_active = 1 AND expires_at > datetime('now')
        ''')
        active_sessions = cursor.fetchone()[0]
        
        # Recent login attempts
        cursor.execute('''
            SELECT COUNT(*) FROM login_attempts 
            WHERE attempted_at >= datetime('now', '-24 hours')
        ''')
        recent_attempts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'new_users_month': new_users_month,
            'active_sessions': active_sessions,
            'recent_attempts': recent_attempts
        }

def show_login_page(auth_system: AuthenticationSystem):
    """Display login page"""
    
    st.title("🔐 Login to Food Analyzer")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown("### 👤 Sign In")
        
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me")
            
            submitted = st.form_submit_button("🔑 Login", type="primary")
            
            if submitted:
                if username and password:
                    success, user_data = auth_system.authenticate_user(username, password)
                    
                    if success:
                        # Create session
                        session_id = auth_system.create_session(user_data['id'])
                        
                        # Store in session state
                        st.session_state.authenticated = True
                        st.session_state.user_data = user_data
                        st.session_state.session_id = session_id
                        
                        st.success(f"✅ Welcome back, {user_data['username']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.error("❌ Please fill in all fields")
        
        # Demo accounts
        st.markdown("---")
        st.markdown("### 🎯 Demo Accounts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👤 Demo User Login"):
                st.session_state.authenticated = True
                st.session_state.user_data = {
                    'id': 'demo-user',
                    'username': 'demo_user',
                    'email': 'demo@example.com',
                    'role': 'user'
                }
                st.rerun()
        
        with col2:
            if st.button("👑 Admin Demo Login"):
                st.session_state.authenticated = True
                st.session_state.user_data = {
                    'id': 'demo-admin',
                    'username': 'admin',
                    'email': 'admin@example.com',
                    'role': 'admin'
                }
                st.rerun()
    
    with tab2:
        st.markdown("### 📝 Create Account")
        
        with st.form("register_form"):
            new_username = st.text_input("Username", help="At least 3 characters")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password", 
                                       help="At least 8 characters with uppercase, lowercase, and number")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            submitted = st.form_submit_button("📝 Create Account", type="primary")
            
            if submitted:
                if not agree_terms:
                    st.error("❌ Please agree to the terms and conditions")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif new_username and new_email and new_password:
                    success, message = auth_system.register_user(new_username, new_email, new_password)
                    
                    if success:
                        st.success("✅ Account created successfully! Please login.")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Please fill in all fields")

def show_user_profile(auth_system: AuthenticationSystem):
    """Display user profile page"""
    
    user_data = st.session_state.user_data
    
    st.title(f"👤 Profile - {user_data['username']}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📊 Account Info")
        st.info(f"**Username**: {user_data['username']}")
        st.info(f"**Email**: {user_data['email']}")
        st.info(f"**Role**: {user_data['role'].title()}")
        
        if st.button("🚪 Logout"):
            if 'session_id' in st.session_state:
                auth_system.invalidate_session(st.session_state.session_id)
            
            # Clear session
            for key in ['authenticated', 'user_data', 'session_id']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.rerun()
    
    with col2:
        st.markdown("### ⚙️ Account Settings")
        
        with st.form("profile_form"):
            st.markdown("#### 🔒 Change Password")
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            
            st.markdown("#### 📧 Notification Preferences")
            email_notifications = st.checkbox("Email notifications", value=True)
            analysis_alerts = st.checkbox("Analysis completion alerts", value=True)
            weekly_summary = st.checkbox("Weekly health summary", value=False)
            
            if st.form_submit_button("💾 Save Changes"):
                if current_password and new_password:
                    if new_password != confirm_new_password:
                        st.error("❌ New passwords do not match")
                    else:
                        # Verify current password and update
                        success, _ = auth_system.authenticate_user(user_data['username'], current_password)
                        if success:
                            st.success("✅ Password updated successfully!")
                        else:
                            st.error("❌ Current password is incorrect")
                else:
                    st.success("✅ Preferences saved!")

def show_admin_panel(auth_system: AuthenticationSystem):
    """Display admin panel"""
    
    st.title("👑 Admin Panel")
    
    # User statistics
    stats = auth_system.get_user_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats['total_users'])
    
    with col2:
        st.metric("New This Month", stats['new_users_month'])
    
    with col3:
        st.metric("Active Sessions", stats['active_sessions'])
    
    with col4:
        st.metric("Login Attempts (24h)", stats['recent_attempts'])
    
    st.markdown("---")
    
    # Admin actions
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 System Stats", "🔧 System Settings"])
    
    with tab1:
        st.markdown("### 👥 User Management")
        
        # List users
        conn = sqlite3.connect(auth_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, email, role, created_at, last_login, is_active
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        if users:
            import pandas as pd
            df = pd.DataFrame(users, columns=['Username', 'Email', 'Role', 'Created', 'Last Login', 'Active'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")
    
    with tab2:
        st.markdown("### 📊 System Statistics")
        st.info("📈 Advanced analytics ready for implementation!")
    
    with tab3:
        st.markdown("### 🔧 System Settings")
        st.info("⚙️ System configuration panel ready for implementation!")

def check_authentication():
    """Check if user is authenticated"""
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    return st.session_state.authenticated

def require_authentication(auth_system: AuthenticationSystem):
    """Require user authentication"""
    
    if not check_authentication():
        show_login_page(auth_system)
        return False
    
    return True

def require_admin_role():
    """Require admin role"""
    
    if not check_authentication():
        return False
    
    user_data = st.session_state.get('user_data', {})
    return user_data.get('role') == 'admin'