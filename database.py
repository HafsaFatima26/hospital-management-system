import sqlite3
import bcrypt
from datetime import datetime
from contextlib import contextmanager

DATABASE = "hospital.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections with foreign keys enabled"""
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    # Enable foreign key constraints per connection as required by SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database schema and seed default users"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create users table with role constraints for RBAC
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin','doctor','receptionist'))
            )
        """)
        
        # Create patients table with anonymization fields for confidentiality
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                anonymized_name TEXT,
                anonymized_contact TEXT,
                encrypted_name TEXT,
                encrypted_contact TEXT,
                date_added TEXT NOT NULL
            )
        """)
        
        # Create logs table with foreign key for integrity and accountability
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Seed default users with hashed passwords (GDPR integrity)
        default_users = [
            ("admin", "admin123", "admin"),
            ("dr_bob", "doc123", "doctor"),
            ("alice_recep", "rec123", "receptionist")
        ]
        
        for username, password, role in default_users:
            try:
                pwd_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, pwd_hash, role)
                )
            except sqlite3.IntegrityError:
                pass  # User already exists
        
        conn.commit()
        print("✅ Database initialized with foreign key constraints enabled")

def add_log(user_id, role, action, details=""):
    """Add audit log entry for accountability (GDPR Article 5)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO logs (user_id, role, action, timestamp, details) VALUES (?, ?, ?, ?, ?)",
            (user_id, role, action, timestamp, details)
        )
        conn.commit()

def get_all_patients():
    """Retrieve all patients for availability"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY date_added DESC")
        return cursor.fetchall()

def get_all_logs():
    """Retrieve audit logs for integrity verification (Admin only)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.log_id, l.user_id, u.username, l.role, l.action, 
                   l.timestamp, l.details
            FROM logs l
            LEFT JOIN users u ON l.user_id = u.user_id
            ORDER BY l.timestamp DESC
        """)
        return cursor.fetchall()

def add_patient(name, contact, diagnosis, anon_name, anon_contact, enc_name="", enc_contact=""):
    """Add new patient with anonymization (GDPR data minimization)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO patients 
            (name, contact, diagnosis, anonymized_name, anonymized_contact, 
             encrypted_name, encrypted_contact, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, contact, diagnosis, anon_name, anon_contact, enc_name, enc_contact, date_added))
        conn.commit()
        return cursor.lastrowid

def update_patient(patient_id, name, contact, diagnosis, anon_name, anon_contact):
    """Update patient record with validation (CIA integrity)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patients 
            SET name=?, contact=?, diagnosis=?, anonymized_name=?, anonymized_contact=?
            WHERE patient_id=?
        """, (name, contact, diagnosis, anon_name, anon_contact, patient_id))
        conn.commit()

def anonymize_all_patients(cipher):
    """Batch anonymize all patients with optional encryption (bonus feature)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id, name, contact FROM patients")
        patients = cursor.fetchall()
        
        for patient in patients:
            pid = patient['patient_id']
            anon_name = f"ANON_{pid:04d}"
            anon_contact = "XXX-XXX-" + patient['contact'][-4:] if len(patient['contact']) >= 4 else "XXX-XXX-XXXX"
            
            # Optional Fernet encryption for reversible anonymization (bonus)
            enc_name = cipher.encrypt(patient['name'].encode()).decode() if cipher else ""
            enc_contact = cipher.encrypt(patient['contact'].encode()).decode() if cipher else ""
            
            cursor.execute("""
                UPDATE patients 
                SET anonymized_name=?, anonymized_contact=?, encrypted_name=?, encrypted_contact=?
                WHERE patient_id=?
            """, (anon_name, anon_contact, enc_name, enc_contact, pid))
        
        conn.commit()
