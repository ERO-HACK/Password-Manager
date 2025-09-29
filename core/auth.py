import os
from core.database import DatabaseManager
from core.encryption import derive_key, encrypt, decrypt

VERIFICATION_TEXT = b"verify"

def register_user(username, master_password):
    db = DatabaseManager()
    if db.get_user(username):
        db.close()
        return False, "User already exists"
    salt = os.urandom(16)
    key = derive_key(master_password, salt)
    verification = encrypt(VERIFICATION_TEXT.decode(), key)  # Encrypt "verify"
    db.insert_user(username, salt, verification)
    db.close()
    return True, "User registered successfully"

def login_user(username, master_password):
    db = DatabaseManager()
    user = db.get_user(username)
    db.close()
    if not user:
        return False, None, None, "User not found"
    user_id, salt, verification = user
    key = derive_key(master_password, salt)
    decrypted = decrypt(verification, key)
    if decrypted == VERIFICATION_TEXT.decode():
        return True, user_id, key, "Login successful"
    return False, None, None, "Invalid password"