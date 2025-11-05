from PIL import Image
import numpy as np

# DELIMITER teks (###) atau gambar (###IMG###)
DELIMITER_BYTES = b"###IMG###"

def to_binary(data):
    """Konversi data string ke biner."""
    if isinstance(data, str):
        return ''.join([format(ord(i), '08b') for i in data])
    else:
        raise TypeError("Tipe data tidak didukung.")

def _get_adaptive_indices(image, threshold_percentile):
    """
    Fungsi helper untuk Adaptive LSB.
    analisis gambar trs return daftar index pixel yang kompleks untuk dimasukin data.
    """
    img_rgb = image.convert('RGB')
    
    # Paksa last bit jadi 0 sebelum analisis.
    pixels = np.array(img_rgb) & 254
    
    # convert ke grayscale buat analisis komplekstas
    gray = np.dot(pixels[...,:3], [0.299, 0.587, 0.114])
    
    # hitung gradien (ukuran kompleksitas)
    gx, gy = np.gradient(gray)
    gradient_mag = np.sqrt(gx**2 + gy**2)
    grad_flat = gradient_mag.flatten()

    # Tentukan threshold berdasarkan persentil
    threshold_val = np.percentile(grad_flat, threshold_percentile)
    embed_indices = np.where(grad_flat >= threshold_val)[0]
    
    np.random.seed(42)
    np.random.shuffle(embed_indices)
    
    # Mengembalikan bentuk asli piksel
    return embed_indices, np.array(img_rgb).shape

def embed_msg(image, secret_message, threshold_percentile):
    img_rgb = image.convert('RGB')
    pixels = np.array(img_rgb)
    flat_pixels = pixels.reshape(-1, 3)

    try:
        embed_indices, shape = _get_adaptive_indices(image, threshold_percentile)
    except Exception as e:
        raise ValueError(f"Gagal menganalisis gambar: {e}")

    secret_message += "###" # Delimiter TEKS
    binary_secret_data = to_binary(secret_message)
    data_len = len(binary_secret_data)
    data_index = 0

    # Cek kapasitas
    total_capacity_bits = len(embed_indices) * 3
    if data_len > total_capacity_bits:
        raise ValueError(f"Error: Pesan terlalu panjang. (Kapasitas: {total_capacity_bits} bit, Pesan: {data_len} bit). Coba turunkan Threshold.")

    # masukin data
    for idx in embed_indices:
        if data_index >= data_len:
            break
        
        pixel = flat_pixels[idx]
        
        for channel in range(3):
            if data_index < data_len:
                val = pixel[channel]
                bit = int(binary_secret_data[data_index])
                
                pixel[channel] = (val & 254) | bit
                data_index += 1
            else:
                break
    
    new_pixels = flat_pixels.reshape(shape)
    return Image.fromarray(new_pixels.astype(np.uint8))


def extract_msg(image, threshold_percentile):
    img_rgb = image.convert('RGB')
    
    try:
        embed_indices, shape = _get_adaptive_indices(image, threshold_percentile)
    except Exception as e:
        raise ValueError(f"Gagal menganalisis gambar: {e}")

    pixels = np.array(img_rgb)
    flat_pixels = pixels.reshape(-1, 3)

    binary_data = ""
    delimiter = "###"
    binary_delimiter = to_binary(delimiter)
    
    for idx in embed_indices:
        pixel = flat_pixels[idx]
        
        for channel in range(3):
            binary_data += str(pixel[channel] & 1)
            
            if binary_data.endswith(binary_delimiter):
                binary_data = binary_data[:-len(binary_delimiter)]
                
                all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
                decoded_data = ""
                for byte in all_bytes:
                    if len(byte) == 8:
                        decoded_data += chr(int(byte, 2))
                
                return decoded_data

    return ""

def bytes_to_binary_string(data_bytes):
    """Konversi data bytes mentah ke string biner"""
    return ''.join(format(byte, '08b') for byte in data_bytes)

def binary_string_to_bytes(binary_string):
    """Konversi string biner balik ke bytes."""
    if len(binary_string) % 8 != 0:
        binary_string = binary_string[:-(len(binary_string) % 8)]
    
    byte_list = []
    for i in range(0, len(binary_string), 8):
        byte_segment = binary_string[i:i+8]
        if len(byte_segment) == 8:
             byte_list.append(int(byte_segment, 2))
    return bytes(byte_list)

def embed_bytes(image, secret_bytes, threshold_percentile):
    img_rgb = image.convert('RGB')
    pixels = np.array(img_rgb)
    flat_pixels = pixels.reshape(-1, 3)

    try:
        embed_indices, shape = _get_adaptive_indices(image, threshold_percentile)
    except Exception as e:
        raise ValueError(f"Gagal menganalisis gambar: {e}")

    # Tambahkan delimiter BYTES
    secret_bytes_with_delimiter = secret_bytes + DELIMITER_BYTES
    binary_secret_data = bytes_to_binary_string(secret_bytes_with_delimiter)
    data_len = len(binary_secret_data)
    data_index = 0

    # Cek kapasitas
    total_capacity_bits = len(embed_indices) * 3
    if data_len > total_capacity_bits:
        raise ValueError(f"Error: Gambar rahasia terlalu besar. (Kapasitas: {total_capacity_bits} bit, Data: {data_len} bit). Coba turunkan Threshold atau gunakan gambar sampul lebih besar.")

    # masukin data (logika sama persis sama yg buat teks)
    for idx in embed_indices:
        if data_index >= data_len:
            break
        
        pixel = flat_pixels[idx]
        
        for channel in range(3):
            if data_index < data_len:
                val = pixel[channel]
                bit = int(binary_secret_data[data_index])
                
                pixel[channel] = (val & 254) | bit
                data_index += 1
            else:
                break
    
    new_pixels = flat_pixels.reshape(shape)
    return Image.fromarray(new_pixels.astype(np.uint8))


def extract_bytes(image, threshold_percentile):
    img_rgb = image.convert('RGB')
    
    try:
        embed_indices, shape = _get_adaptive_indices(image, threshold_percentile)
    except Exception as e:
        raise ValueError(f"Gagal menganalisis gambar: {e}")

    pixels = np.array(img_rgb)
    flat_pixels = pixels.reshape(-1, 3)

    binary_data = ""
    # Cari delimiter BYTES
    binary_delimiter = bytes_to_binary_string(DELIMITER_BYTES)
    
    for idx in embed_indices:
        pixel = flat_pixels[idx]
        
        for channel in range(3):
            binary_data += str(pixel[channel] & 1)
            
            if binary_data.endswith(binary_delimiter):
                binary_data_without_delimiter = binary_data[:-len(binary_delimiter)]
                
                try:
                    decoded_bytes = binary_string_to_bytes(binary_data_without_delimiter)
                    return decoded_bytes
                except Exception as e:
                    print(f"Error saat konversi biner ke bytes: {e}")
                    return None

    return None