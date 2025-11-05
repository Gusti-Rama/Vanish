from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt_bytes(data_bytes, key):
    """
    ambil data sebagai bytes dan kunci, 
    return IV + Ciphertext sebagai bytes.
    """
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    # Generate IV baru setiap kali enkripsi
    iv = get_random_bytes(Blowfish.block_size)
    cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
    
    # Padding buat mastiin ukuran blok sesuai (8 byte)
    padded_data = pad(data_bytes, Blowfish.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    return iv + ciphertext

def decrypt_bytes(encrypted_bytes, key):
    if isinstance(key, str):
        key = key.encode('utf-8')

    # Ekstrak IV dan ciphertext dari data
    iv = encrypted_bytes[:Blowfish.block_size]
    ciphertext = encrypted_bytes[Blowfish.block_size:]

    cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
    
    # Dekripsi data dan hilangkan padding
    decrypted_data = unpad(cipher.decrypt(ciphertext), Blowfish.block_size)
    
    return decrypted_data