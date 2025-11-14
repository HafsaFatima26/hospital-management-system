from cryptography.fernet import Fernet
import os

# Generate or load Fernet key (store securely in production - not hardcoded)
KEY_FILE = "fernet.key"

def get_or_create_key():
    """Generate or load Fernet encryption key (bonus feature)"""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key

def get_cipher():
    """Return Fernet cipher for reversible encryption (GDPR pseudonymisation Article 4(5))"""
    key = get_or_create_key()
    return Fernet(key)

def mask_name(patient_id):
    """Generate anonymized name (GDPR data minimization)"""
    return f"ANON_{patient_id:04d}"

def mask_contact(contact):
    """Mask contact number for confidentiality (CIA triad)"""
    if len(contact) >= 4:
        return "XXX-XXX-" + contact[-4:]
    return "XXX-XXX-XXXX"

def decrypt_field(cipher, encrypted_value):
    """Decrypt Fernet-encrypted field (Admin only, logged action)"""
    try:
        if encrypted_value:
            return cipher.decrypt(encrypted_value.encode()).decode()
        return ""
    except Exception as e:
        return f"[Decryption Error: {e}]"
