# Fungsi Helper
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
    d = mod_inverse(e, phi)
    
    public_key = (e, n)
    private_key = (d, n)
    
    return public_key, private_key

# (e=17, n=3233) public key
# (d=2753, n=3233) private key
PUBLIC_KEY, PRIVATE_KEY = rsa_generate_keys()


def rsa_encrypt(message):
    """
    Mengenkripsi pesan menggunakan kunci publik yang sudah 
    didefinisikan di file ini.
    """
    e, n = PUBLIC_KEY # Ambil kunci yang sudah didefinisikan
    
    # Enkripsi setiap karakter menjadi angka menggunakan RSA
    encrypted = [pow(ord(char), e, n) for char in message]
    return encrypted

def rsa_decrypt(encrypted):
    """
    Mendekripsi pesan menggunakan kunci privat yang sudah
    didefinisikan di file ini.
    """
    d, n = PRIVATE_KEY # Ambil kunci yang sudah didefinisikan
    
    if isinstance(encrypted, str):
        encrypted_list = encrypted.split()
    else:
        # Jika input sudah berupa list, langsung gunakan
        encrypted_list = encrypted
    
    # Dekripsi setiap angka kembali menjadi karakter
    decrypted = ''.join(chr(pow(int(char), d, n)) for char in encrypted_list)
    return decrypted