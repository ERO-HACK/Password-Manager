import secrets
import string

def generate_password(length=16, include_upper=True, include_lower=True, include_digits=True, include_symbols=True):
    characters = ''
    if include_upper:
        characters += string.ascii_uppercase
    if include_lower:
        characters += string.ascii_lowercase
    if include_digits:
        characters += string.digits
    if include_symbols:
        characters += string.punctuation
    if not characters:
        raise ValueError("At least one character type must be selected")
    return ''.join(secrets.choice(characters) for _ in range(length))