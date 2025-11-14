# 🏥 GDPR-Compliant Hospital Management System

**Information Security (CS-3002) - Assignment 4**  
Privacy, Trust & the CIA Triad in Modern Information Systems

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red.svg)](https://streamlit.io/)
[![GDPR Compliant](https://img.shields.io/badge/GDPR-compliant-green.svg)](https://gdpr-info.eu/)

## Project Overview

A comprehensive hospital management system implementing the **CIA Triad** (Confidentiality, Integrity, Availability) with full **GDPR Article 5** compliance. Inspired by RSA Conference 2024 presentation on data privacy evolution.

### Key Features

- **Confidentiality**: bcrypt password hashing, Fernet encryption, data masking
- **Integrity**: Comprehensive audit logging, database constraints, RBAC
- **Availability**: Error handling, CSV exports, session management
- **GDPR Compliance**: Consent banner, data retention, pseudonymisation
- **Bonus Features**: Real-time activity graphs, automated data deletion

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
git clone https://github.com/YOUR_USERNAME/hospital-management-system.git
cd hospital-management-system


2. **Create virtual environment**
Windows
python -m venv venv
venv\Scripts\activate

macOS/Linux
python3 -m venv venv
source venv/bin/activate


3. **Install dependencies**
pip install -r requirements.txt



4. **Run the application**
streamlit run app.py


5. **Access the app**
Open browser at: http://localhost:8501

##  Default Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| **Admin** | `admin` | `admin123` | Full system access, raw data, audit logs |
| **Doctor** | `dr_bob` | `doc123` | Anonymized patient data only |
| **Receptionist** | `alice_recep` | `rec123` | Add/edit patients, no viewing |

##  Project Structure
hospital-management-system/
├── app.py # Main Streamlit application
├── database.py # Database operations & schema
├── auth.py # Authentication & RBAC
├── crypto_utils.py # Encryption & anonymization
├── requirements.txt # Python dependencies
├── README.md # Project documentation
└── .gitignore # Git ignore rules


## 🛡️ CIA Triad Implementation

### Confidentiality
- **bcrypt** password hashing with salt
- **Fernet** (AES-128) encryption for reversible anonymization
- Data masking: `ANON_xxxx`, `XXX-XXX-4592`
- Role-based access control (RBAC)
- 30-minute session timeout

### Integrity
- Comprehensive audit logging (all actions tracked)
- Database constraints: `CHECK`, `FOREIGN KEY`
- `PRAGMA foreign_keys=ON` enforcement
- Input validation and sanitization
- Admin-only audit log access

### Availability
- Try-except error handling on all operations
- CSV export for data backup/recovery
- Uptime monitoring and display
- Graceful degradation on failures

## 🇪🇺 GDPR Compliance

Implements all GDPR Article 5 principles:

- ✅ **Lawfulness, Fairness, Transparency**: Consent banner, audit logs
- ✅ **Purpose Limitation**: Healthcare-only data usage
- ✅ **Data Minimisation**: Anonymization, diagnosis masking
- ✅ **Accuracy**: Update workflows with validation
- ✅ **Storage Limitation**: Automated data retention (30-3650 days)
- ✅ **Integrity & Confidentiality**: Encryption + RBAC
- ✅ **Accountability**: Immutable audit trail

## Features

### Core Features
- [x] SQLite database with foreign key constraints
- [x] Three-tier RBAC (Admin/Doctor/Receptionist)
- [x] Patient data anonymization
- [x] Secure audit logging
- [x] Error handling & recovery

### Bonus Features
- [x] Fernet encryption for reversible anonymization
- [x] Real-time activity graphs (actions/day, by type, by role)
- [x] Automated data retention with configurable period
- [x] GDPR consent banner on login

## Testing

Run the application and test all roles:

1. Login as **Admin** → View raw data, trigger anonymization, check audit logs
2. Login as **Doctor** → Verify only anonymized data visible
3. Login as **Receptionist** → Add patient, verify cannot view records
4. Wait 30 minutes → Verify session timeout
5. Settings page → Test data retention deletion

## Documentation

- **Report**: Hospital_Management_System_Report.pdf (10 pages)
- **Implementation Guide**: Complete setup instructions
- **Requirements Matrix**: All 32 requirements verified

## Contributing

This is an academic project for CS-3002 Information Security course.

## Authors

- [Your Name] - Student ID
- [Partner Name] - Student ID

**Institution**: [Your University Name]  
**Course**: Information Security (CS-3002)  
**Instructor**: [Instructor Name]  
**Date**: November 14, 2025

## License

This project is submitted as coursework for educational purposes.

## Acknowledgments

- RSA Conference 2024: "Privacy Past and Present" presentation
- GDPR Article 5 principles and guidelines
- CIA Triad security framework
- Streamlit, Cryptography, bcrypt, pandas libraries

## Contact

For questions or issues, contact: [your.email@university.edu]

---

**Security Notice**: This is a demonstration project. For production use, implement additional security measures including SSL/TLS, database encryption at rest, and professional key management.
