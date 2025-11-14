import sqlite3
import bcrypt
from database import get_db_connection, add_log

def authenticate_user(username, password):
    """Authenticate user with bcrypt hashing (CIA confidentiality)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, password_hash, role FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
                return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'role': user['role']
                }
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def check_role(session_state, required_roles):
    """RBAC middleware - restrict access by role (CIA confidentiality & integrity)"""
    if 'user' not in session_state or session_state['user'] is None:
        return False
    return session_state['user']['role'] in required_roles

def log_user_action(session_state, action, details=""):
    """Log user actions for audit trail (GDPR accountability)"""
    if 'user' in session_state and session_state['user']:
        user = session_state['user']
        add_log(user['user_id'], user['role'], action, details)
