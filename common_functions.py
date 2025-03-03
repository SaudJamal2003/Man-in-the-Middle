# common_functions.py

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def generate_digital_signature(message, private_key_data):
    """Generates a digital signature for the given message using the private key."""
    private_key = RSA.import_key(private_key_data)
    h = SHA256.new(message.encode())
    signature = pkcs1_15.new(private_key).sign(h)
    return signature

def verify_digital_signature(message, signature, public_key_data):
    """Verifies the digital signature of a message using the public key."""
    public_key = RSA.import_key(public_key_data)
    h = SHA256.new(message.encode())
    
    try:
        pkcs1_15.new(public_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False
