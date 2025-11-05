from PIL import Image
import numpy as np

def to_binary(data):
    """Konversi data string ke biner."""
    if isinstance(data, str):
        return ''.join([format(ord(i), '08b') for i in data])
    else:
        raise TypeError("Tipe data tidak didukung.")

def _get_adaptive_indices(image, threshold_percentile):
    """
    Fungsi helper untuk Adaptive LSB.
    Menganalisis gambar dan mengembalikan daftar indeks piksel 
    yang "kompleks" (aman) untuk disisipi data.
    """
    img_rgb = image.convert('RGB')
    
    # Paksa LSB (bit terakhir) menjadi 0 sebelum analisis.
    pixels = np.array(img_rgb) & 254
    
    # Konversi ke grayscale untuk analisis kompleksitas
    gray = np.dot(pixels[...,:3], [0.299, 0.587, 0.114])
    
    # Hitung gradien (ukuran kompleksitas)
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
    """
    Menyembunyikan pesan rahasia ke dalam gambar menggunakan Adaptive LSB.
    """
    img_rgb = image.convert('RGB')
    pixels = np.array(img_rgb)
    flat_pixels = pixels.reshape(-1, 3)

    try:
        embed_indices, shape = _get_adaptive_indices(image, threshold_percentile)
    except Exception as e:
        raise ValueError(f"Gagal menganalisis gambar: {e}")

    secret_message += "###" # Delimiter
    binary_secret_data = to_binary(secret_message)
    data_len = len(binary_secret_data)
    data_index = 0

    # Cek kapasitas
    total_capacity_bits = len(embed_indices) * 3
    if data_len > total_capacity_bits:
        raise ValueError(f"Error: Pesan terlalu panjang. (Kapasitas: {total_capacity_bits} bit, Pesan: {data_len} bit). Coba turunkan Threshold.")

    # Sisipkan data
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
    
    # Kembalikan gambar baru
    new_pixels = flat_pixels.reshape(shape)
    return Image.fromarray(new_pixels.astype(np.uint8))


def extract_msg(image, threshold_percentile):
    """
    Mengekstrak pesan rahasia dari gambar menggunakan Adaptive LSB.
    """
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