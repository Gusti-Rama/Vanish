from PIL import Image
import numpy as np

def genData(data):
    return [format(ord(i), '08b') for i in data]

def embed_msg(image_path, output_path, message):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = np.array(img)
    h, w, _ = pixels.shape
    flat_pixels = pixels.reshape(-1, 3)
    
    if not message:
        raise ValueError("Message cannot be empty.")
    
    data_bits = ''.join(genData(message + '###'))
    bit_idx = 0
    total_bits = len(data_bits)

    # Compute gradient magnitude to find "complex" regions
    gray = np.dot(pixels[..., :3], [0.299, 0.587, 0.114])
    gx, gy = np.gradient(gray)
    gradient_mag = np.sqrt(gx**2 + gy**2)
    grad_flat = gradient_mag.flatten()

    # Normalize and create mask for complex pixels
    threshold = np.percentile(grad_flat, 60)  # top 40% = embed area
    embed_indices = np.where(grad_flat >= threshold)[0]

    # Shuffle indices (optional for extra stealth)
    # np.random.seed(42)
    # np.random.shuffle(embed_indices)

    for idx in embed_indices:
        if bit_idx >= total_bits:
            break
        for channel in range(3):
            if bit_idx >= total_bits:
                break
            val = flat_pixels[idx][channel]
            bit = int(data_bits[bit_idx])
            flat_pixels[idx][channel] = (val & ~1) | bit
            bit_idx += 1

    if bit_idx < total_bits:
        raise ValueError("Message too long for this image!")

    new_pixels = flat_pixels.reshape(h, w, 3)
    new_img = Image.fromarray(new_pixels.astype(np.uint8))
    new_img.save(output_path)
    return output_path


def extract_msg(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = np.array(img)
    flat_pixels = pixels.reshape(-1, 3)
    bits = ''
    for r, g, b in flat_pixels:
        bits += str(r & 1)
        bits += str(g & 1)
        bits += str(b & 1)

    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    decoded = ''.join([chr(int(c, 2)) for c in chars])
    end = decoded.find('###')
    return decoded[:end] if end != -1 else decoded
