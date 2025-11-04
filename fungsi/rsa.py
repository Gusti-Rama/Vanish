def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(e, phi):
    for d in range(1, phi):
        if (e * d) % phi == 1:
            return d
    return -1

def rsa_generate_keys():
    p = 61
    q = 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17

    # Mencari d (kunci privat)
    d = mod_inverse(e, phi)
    
    public_key = (e, n)
    private_key = (d, n)
    
    return public_key, private_key

def rsa_encrypt(message, key):
    e, n = key
    # Enkripsi setiap karakter menjadi angka menggunakan RSA
    encrypted = [pow(ord(char), e, n) for char in message]
    return encrypted

def rsa_decrypt(encrypted, key):
    d, n = key
    # Jika input berupa string, ubah menjadi list menggunakan split()
    if isinstance(encrypted, str):
        encrypted_list = encrypted.split()
    else:
        # Jika input sudah berupa list, langsung gunakan
        encrypted_list = encrypted
    
    # Dekripsi setiap angka kembali menjadi karakter
    decrypted = ''.join(chr(pow(int(char), d, n)) for char in encrypted_list)
    return decrypted
