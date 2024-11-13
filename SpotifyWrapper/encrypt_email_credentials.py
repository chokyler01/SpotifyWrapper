from cryptography.fernet import Fernet

# Generate a key for encryption and save it in a file
key = Fernet.generate_key()
with open("email_key.key", "wb") as key_file:
    key_file.write(key)

# Create a Fernet cipher instance
cipher = Fernet(key)

# Email credentials to encrypt
email_user = "chokyler01@gmail.com"
email_password = "Chom22@gsis"

# Encrypt the credentials
encrypted_email_user = cipher.encrypt(email_user.encode())
encrypted_email_password = cipher.encrypt(email_password.encode())

# Save the encrypted credentials to a file
with open("encrypted_email_credentials.txt", "wb") as encrypted_file:
    encrypted_file.write(encrypted_email_user + b"\n" + encrypted_email_password)

print("Credentials encrypted and saved successfully.")
