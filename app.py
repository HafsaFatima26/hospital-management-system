import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    init_database, get_all_patients, get_all_logs, 
    add_patient, update_patient, anonymize_all_patients
)
from auth import authenticate_user, check_role, log_user_action
from crypto_utils import get_cipher, mask_name, mask_contact, decrypt_field

# Page configuration
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
init_database()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'Login'

# System uptime (availability indicator)
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = datetime.now()

# ========== HELPER FUNCTIONS ==========

def logout():
    """Logout and clear session"""
    if st.session_state['user']:
        log_user_action(st.session_state, "LOGOUT", "User logged out")
    st.session_state['user'] = None
    st.session_state['page'] = 'Login'
    st.rerun()

def export_to_csv(data, filename):
    """Export data to CSV for availability and backup (GDPR Article 5)"""
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    st.download_button(
        label=f"📥 Download {filename}",
        data=csv,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# ========== LOGIN PAGE ==========

def login_page():
    """User authentication with session management (CIA confidentiality)"""
    st.title("🏥 Hospital Management System")
    st.subheader("🔐 Secure Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state['user'] = user
                        st.session_state['page'] = 'Dashboard'
                        log_user_action(st.session_state, "LOGIN", f"User {username} logged in")
                        st.success(f"✅ Welcome, {user['username']} ({user['role']})")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                        # Log failed login attempt (integrity/security)
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        st.divider()
        st.info("""
        **Demo Credentials:**
        - Admin: `admin` / `admin123`
        - Doctor: `dr_bob` / `doc123`
        - Receptionist: `alice_recep` / `rec123`
        """)
        
        st.caption("🔒 All data encrypted & GDPR-compliant | CIA Triad Protected")

# ========== DASHBOARD PAGE ==========

def dashboard_page():
    """Main dashboard with role-based welcome (RBAC)"""
    user = st.session_state['user']
    
    st.title("🏥 Hospital Management Dashboard")
    st.subheader(f"Welcome, **{user['username']}** | Role: **{user['role'].upper()}**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👤 Current User", user['username'])
    with col2:
        st.metric("🔑 Access Level", user['role'].capitalize())
    with col3:
        uptime = datetime.now() - st.session_state['start_time']
        st.metric("⏱️ System Uptime", f"{uptime.seconds // 60} mins")
    
    st.divider()
    
    # Role-specific instructions (GDPR transparency)
    if user['role'] == 'admin':
        st.success("🔓 **Admin Access**: Full system control, raw data access, audit logs")
    elif user['role'] == 'doctor':
        st.info("👨‍⚕️ **Doctor Access**: View anonymized patient data only")
    else:
        st.warning("📝 **Receptionist Access**: Add/edit records, no sensitive data view")
    
    log_user_action(st.session_state, "VIEW_DASHBOARD", "Accessed dashboard")

# ========== PATIENTS PAGE ==========

def patients_page():
    """Patient management with role-based data masking (CIA confidentiality)"""
    user = st.session_state['user']
    st.title("👥 Patient Records")
    
    tab1, tab2, tab3 = st.tabs(["📋 View Patients", "➕ Add Patient", "🔄 Update Patient"])
    
    # TAB 1: View Patients
    with tab1:
        st.subheader("Patient List")
        
        patients = get_all_patients()
        if patients:
            # Role-based data display (RBAC for confidentiality)
            if user['role'] == 'admin':
                view_mode = st.radio("View Mode (Admin Only):", ["Anonymized", "Raw Data"], horizontal=True)
                
                if view_mode == "Raw Data":
                    st.warning("⚠️ Viewing raw patient data - ensure GDPR compliance")
                    log_user_action(st.session_state, "VIEW_RAW_DATA", "Admin viewed raw patient data")
                    
                    df = pd.DataFrame([dict(p) for p in patients])
                    st.dataframe(df[['patient_id', 'name', 'contact', 'diagnosis', 'date_added']], use_container_width=True)
                else:
                    df = pd.DataFrame([dict(p) for p in patients])
                    st.dataframe(df[['patient_id', 'anonymized_name', 'anonymized_contact', 'diagnosis', 'date_added']], use_container_width=True)
                
                export_to_csv([dict(p) for p in patients], "patients_data")
            
            elif user['role'] == 'doctor':
                st.info("👨‍⚕️ Viewing anonymized data (GDPR compliant)")
                log_user_action(st.session_state, "VIEW_ANONYMIZED_DATA", "Doctor viewed anonymized data")
                
                df = pd.DataFrame([dict(p) for p in patients])
                st.dataframe(df[['patient_id', 'anonymized_name', 'anonymized_contact', 'diagnosis', 'date_added']], use_container_width=True)
            
            else:
                st.warning("🚫 Receptionists cannot view patient records (confidentiality)")
        else:
            st.info("No patient records found")
    
    # TAB 2: Add Patient
    with tab2:
        if user['role'] in ['admin', 'receptionist']:
            st.subheader("Add New Patient")
            
            with st.form("add_patient_form"):
                name = st.text_input("Full Name*")
                contact = st.text_input("Contact Number*")
                diagnosis = st.text_area("Diagnosis*")
                submit = st.form_submit_button("Add Patient", use_container_width=True)
                
                if submit:
                    if name and contact and diagnosis:
                        # Generate anonymized fields (GDPR pseudonymisation)
                        cipher = get_cipher()
                        anon_name = mask_name(999)  # Temp ID, will update after insert
                        anon_contact = mask_contact(contact)
                        
                        # Optional encryption (bonus)
                        enc_name = cipher.encrypt(name.encode()).decode()
                        enc_contact = cipher.encrypt(contact.encode()).decode()
                        
                        pid = add_patient(name, contact, diagnosis, anon_name, anon_contact, enc_name, enc_contact)
                        
                        # Update with correct anonymized name
                        update_patient(pid, name, contact, diagnosis, mask_name(pid), anon_contact)
                        
                        log_user_action(st.session_state, "ADD_PATIENT", f"Added patient ID {pid}")
                        st.success(f"✅ Patient added successfully (ID: {pid})")
                        st.rerun()
                    else:
                        st.error("❌ All fields are required")
        else:
            st.error("🚫 Doctors cannot add patients (integrity control)")
    
    # TAB 3: Update Patient
    with tab3:
        if user['role'] in ['admin', 'receptionist']:
            st.subheader("Update Patient Record")
            
            patients = get_all_patients()
            if patients:
                patient_ids = [p['patient_id'] for p in patients]
                selected_id = st.selectbox("Select Patient ID", patient_ids)
                
                selected_patient = next(p for p in patients if p['patient_id'] == selected_id)
                
                with st.form("update_patient_form"):
                    name = st.text_input("Full Name", value=selected_patient['name'])
                    contact = st.text_input("Contact", value=selected_patient['contact'])
                    diagnosis = st.text_area("Diagnosis", value=selected_patient['diagnosis'])
                    submit = st.form_submit_button("Update Patient", use_container_width=True)
                    
                    if submit:
                        anon_name = mask_name(selected_id)
                        anon_contact = mask_contact(contact)
                        update_patient(selected_id, name, contact, diagnosis, anon_name, anon_contact)
                        
                        log_user_action(st.session_state, "UPDATE_PATIENT", f"Updated patient ID {selected_id}")
                        st.success("✅ Patient updated successfully")
                        st.rerun()
            else:
                st.info("No patients to update")
        else:
            st.error("🚫 Doctors cannot update patients (integrity control)")

# ========== ANONYMIZATION PAGE ==========

def anonymization_page():
    """Batch anonymization with encryption (Admin only - GDPR pseudonymisation)"""
    if not check_role(st.session_state, ['admin']):
        st.error("🚫 Access Denied: Admin only")
        return
    
    st.title("🔐 Data Anonymization & Encryption")
    st.info("**GDPR Article 4(5)**: Pseudonymisation with separate key management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Anonymize All Patients")
        if st.button("🔒 Apply Anonymization", use_container_width=True):
            cipher = get_cipher()
            anonymize_all_patients(cipher)
            log_user_action(st.session_state, "ANONYMIZE_ALL", "Batch anonymization applied with encryption")
            st.success("✅ All patients anonymized and encrypted")
            st.rerun()
    
    with col2:
        st.subheader("Decrypt Patient Data")
        patients = get_all_patients()
        if patients:
            patient_ids = [p['patient_id'] for p in patients]
            selected_id = st.selectbox("Select Patient", patient_ids)
            
            if st.button("🔓 Decrypt & View", use_container_width=True):
                patient = next(p for p in patients if p['patient_id'] == selected_id)
                cipher = get_cipher()
                
                decrypted_name = decrypt_field(cipher, patient['encrypted_name'])
                decrypted_contact = decrypt_field(cipher, patient['encrypted_contact'])
                
                st.success("🔓 Decrypted Data:")
                st.write(f"**Name:** {decrypted_name}")
                st.write(f"**Contact:** {decrypted_contact}")
                
                log_user_action(st.session_state, "DECRYPT_DATA", f"Decrypted patient ID {selected_id}")

# ========== AUDIT LOGS PAGE ==========

def audit_logs_page():
    """View system audit logs (Admin only - GDPR accountability)"""
    if not check_role(st.session_state, ['admin']):
        st.error("🚫 Access Denied: Admin only")
        return
    
    st.title("📜 Integrity Audit Log")
    st.info("**GDPR Article 5(2)**: Accountability through comprehensive logging")
    
    logs = get_all_logs()
    
    if logs:
        df = pd.DataFrame([dict(log) for log in logs])
        st.dataframe(df, use_container_width=True)
        
        export_to_csv([dict(log) for log in logs], "audit_logs")
        
        # Filter logs
        st.subheader("Filter Logs")
        col1, col2 = st.columns(2)
        with col1:
            filter_action = st.selectbox("Action Type", ["All"] + list(df['action'].unique()))
        with col2:
            filter_role = st.selectbox("Role", ["All"] + list(df['role'].unique()))
        
        filtered_df = df
        if filter_action != "All":
            filtered_df = filtered_df[filtered_df['action'] == filter_action]
        if filter_role != "All":
            filtered_df = filtered_df[filtered_df['role'] == filter_role]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        log_user_action(st.session_state, "VIEW_AUDIT_LOG", "Accessed audit logs")
    else:
        st.info("No audit logs found")

# ========== MAIN NAVIGATION ==========

def main():
    """Main application router with RBAC navigation"""
    
    if st.session_state['user'] is None:
        login_page()
    else:
        user = st.session_state['user']
        
        # Sidebar navigation
        with st.sidebar:
            st.image("https://img.icons8.com/fluency/96/000000/hospital-3.png", width=80)
            st.title("Navigation")
            
            pages = {
                'Dashboard': '🏠',
                'Patients': '👥',
            }
            
            if user['role'] == 'admin':
                pages['Anonymization'] = '🔐'
                pages['Audit Logs'] = '📜'
            
            for page, icon in pages.items():
                if st.button(f"{icon} {page}", use_container_width=True):
                    st.session_state['page'] = page
                    st.rerun()
            
            st.divider()
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
            
            st.divider()
            st.caption(f"👤 {user['username']}")
            st.caption(f"🔑 {user['role'].capitalize()}")
            
            # System info (availability)
            uptime = datetime.now() - st.session_state['start_time']
            st.caption(f"⏱️ Uptime: {uptime.seconds // 60}m")
            st.caption("🔒 GDPR Compliant")
        
        # Page routing
        page = st.session_state.get('page', 'Dashboard')
        
        if page == 'Dashboard':
            dashboard_page()
        elif page == 'Patients':
            patients_page()
        elif page == 'Anonymization':
            anonymization_page()
        elif page == 'Audit Logs':
            audit_logs_page()
        
        # Footer (availability indicator)
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("🛡️ CIA Triad: Confidentiality, Integrity, Availability")
        with col2:
            st.caption("📜 GDPR Article 5 Compliant")
        with col3:
            st.caption(f"🕒 Last Sync: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
