import hashlib
from Crypto.Cipher import AES, Blowfish
from Crypto.Util.Padding import pad, unpad
import base64
import os

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash):
    """Verify password against hash"""
    return hash_password(password) == hash

class AESCipher:
    def __init__(self, key):
        """Initialize AES object with a key"""
        self.key = hashlib.sha256(key.encode()).digest()[:16]  # For AES-128
        
    def encrypt(self, data):
        """Encrypt data using AES-128-CBC"""
        iv = os.urandom(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(pad(data.encode(), AES.block_size))).decode()
    
    def decrypt(self, enc):
        """Decrypt data using AES-128-CBC"""
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[AES.block_size:]), AES.block_size).decode()

class BlowfishCipher:
    def __init__(self, key):
        """Initialize Blowfish object with a key"""
        self.key = hashlib.sha256(key.encode()).digest()[:16]
        
    def encrypt_file(self, file_data):
        """Encrypt file data using Blowfish"""
        iv = os.urandom(Blowfish.block_size)
        cipher = Blowfish.new(self.key, Blowfish.MODE_CBC, iv)
        padded_data = pad(file_data, Blowfish.block_size)
        return base64.b64encode(iv + cipher.encrypt(padded_data)).decode()
    
    def decrypt_file(self, enc_data):
        """Decrypt file data using Blowfish"""
        enc = base64.b64decode(enc_data)
        iv = enc[:Blowfish.block_size]
        cipher = Blowfish.new(self.key, Blowfish.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[Blowfish.block_size:]), Blowfish.block_size)