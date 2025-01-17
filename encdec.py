from cryptography.fernet import Fernet

def generate_key():
    """
    Generate a key for encryption and save it to a file (optional).
    This key must be kept secure as it is required for decryption.
    """
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    """
    Load the previously generated key from a file.
    """
    with open("secret.key", "rb") as key_file:
        key = key_file.read()
    return key

def encrypt_string(plain_text):
    """
    Encrypt a string using the Fernet symmetric encryption.
    
    Args:
        plain_text (str): The plain text string to encrypt.

    Returns:
        str: The encrypted string.
    """
    key = load_key()  # Ensure the key is generated and saved beforehand
    fernet = Fernet(key)
    encrypted = fernet.encrypt(plain_text.encode())
    return encrypted.decode()

def decrypt_string(encrypted_text):
    """
    Decrypt a string using the Fernet symmetric encryption.
    
    Args:
        encrypted_text (str): The encrypted string to decrypt.

    Returns:
        str: The decrypted string.
    """
    
    key = load_key()  # Ensure the key is the same used for encryption
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_text.encode())
    return decrypted.decode()

# Example Usage
if __name__ == "__main__":
    # Generate and save the key (do this once and keep the key secure)
    # Uncomment the line below to generate the key for the first time
    # generate_key()
    
    # Encrypt a string
    generate_key()
    plain_text = "MySecretPassword123"
    encrypted_text = encrypt_string(plain_text)
    print(f"Encrypted: {encrypted_text}")
    
    # Decrypt the string
    decrypted_text = decrypt_string(encrypted_text)
    print(f"Decrypted: {decrypted_text}")
