import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

def get_decrypted_credentials():
    # Load the encryption key and encrypted credentials
    encryption_key = os.getenv('ENCRYPTION_KEY').encode()
    encrypted_client_id = os.getenv('ENCRYPTED_SPOTIFY_CLIENT_ID').encode()
    encrypted_client_secret = os.getenv('ENCRYPTED_SPOTIFY_CLIENT_SECRET').encode()

    # Initialize Fernet and decrypt the credentials
    fernet = Fernet(encryption_key)
    client_id = fernet.decrypt(encrypted_client_id).decode()
    client_secret = fernet.decrypt(encrypted_client_secret).decode()

    return client_id, client_secret
