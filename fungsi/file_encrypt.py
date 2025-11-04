from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad

def encrypt_file(file, key):
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    cipher = Blowfish.new(key, Blowfish.MODE_CBC)
    iv = cipher.iv
    
    # Membaca konten dari file yang diunggah
    plaintext = file.read()
    
    # Padding untuk memastikan ukuran blok sesuai dengan Blowfish (8 byte)
    padded_data = pad(plaintext, Blowfish.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    # Mendapatkan ekstensi file asli
    original_filename = file.name
    original_extension = original_filename.split('.')[-1]
    encrypted_filename = f"{original_filename.rsplit('.', 1)[0]}_{original_extension}_encrypted.bin"
    
    # Menulis data terenkripsi ke file output dalam format biner
    with open(encrypted_filename, 'wb') as out_file:
        out_file.write(iv + ciphertext)

    return encrypted_filename  # Mengembalikan path file terenkripsi

def decrypt_file(file, key):
    if isinstance(key, str):
        key = key.encode('utf-8')

    # Membaca konten dari file yang diunggah
    file_content = file.read()
    
    # Ekstrak IV dan ciphertext dari file terenkripsi
    iv = file_content[:Blowfish.block_size]
    ciphertext = file_content[Blowfish.block_size:]

    # Inisialisasi cipher dengan Blowfish
    cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
    
    # Dekripsi data dan hilangkan padding
    decrypted_data = unpad(cipher.decrypt(ciphertext), Blowfish.block_size)
    
    # Mendapatkan nama file asli dan ekstensi dari nama file terenkripsi
    original_filename = file.name
    # Ekstrak ekstensi asli dari file terenkripsi
    original_extension = original_filename.split('_')[-2]
    decrypted_filename = f"{original_filename.rsplit('_', 2)[0]}.{original_extension}"
    
    # Menulis data yang terdekripsi ke file output dengan ekstensi asli
    with open(decrypted_filename, 'wb') as out_file:
        out_file.write(decrypted_data)

    return decrypted_filename  # Mengembalikan path file yang telah didekripsi
