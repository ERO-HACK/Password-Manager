from cryptography.fernet import Fernet, InvalidToken
import hashlib
import os
import base64

def derive_key(password, salt):
    # Derive a 32-byte key using PBKDF2
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
    # Fernet expects base64 urlsafe encoded key
    return base64.urlsafe_b64encode(key)

def encrypt(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt(encrypted_data, key):
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_data).decode()
    except InvalidToken:
        return None