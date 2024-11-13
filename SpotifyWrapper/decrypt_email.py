from cryptography.fernet import Fernet

def load_key():
    """Load the encryption key from a file."""
    with open("email_key.key", "rb") as key_file:
        return key_file.read()

def decrypt_email_credentials():
    """Decrypt the email credentials."""
    # Load the encryption key and create a Fernet cipher instance
    key = load_key()
    cipher = Fernet(key)

    # Read the encrypted email credentials
    with open("encrypted_email_credentials.txt", "rb") as encrypted_file:
        encrypted_data = encrypted_file.readlines()
        encrypted_email_user = encrypted_data[0].strip()
        encrypted_email_password = encrypted_data[1].strip()

    # Decrypt the credentials
    email_user = cipher.decrypt(encrypted_email_user).decode()
    email_password = cipher.decrypt(encrypted_email_password).decode()

    return email_user, email_password
