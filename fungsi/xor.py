def xor_encrypt(text, key):
    key = str(key)
    encrypted = ''
    for i in range(len(text)):
        encrypted += chr(ord(text[i]) ^ ord(key[i % len(key)]))
    return encrypted

def xor_decrypt(encrypted_text, key):
    return xor_encrypt(encrypted_text, key)  # XOR is symmetric
