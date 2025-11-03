from PIL import Image
import numpy as np

def to_binary(data):
    """Convert data to binary format"""
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes):
        return ''.join([format(i, "08b") for i in data])
    elif isinstance(data, np.ndarray):
        return [format(i, "08b") for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")

def encode_image(image_path, secret_data, output_path):
    """Encode secret data into image using LSB steganography"""
    # Read the image
    image = Image.open(image_path)
    image_array = np.array(image)
    
    # Check if the image can hold the data
    n_bytes = image_array.shape[0] * image_array.shape[1] * 3 // 8
    if len(secret_data) > n_bytes:
        raise ValueError("Error: Insufficient bytes, need bigger image or less data!")

    # Add stopping criteria
    secret_data += "====="
    
    # Convert data to binary
    binary_secret_data = to_binary(secret_data)
    data_len = len(binary_secret_data)
    
    # Modify pixels
    data_index = 0
    for i in range(image_array.shape[0]):
        for j in range(image_array.shape[1]):
            # Modify RGB values
            for k in range(3):
                if data_index < data_len:
                    # Get the binary value of the pixel
                    binary_pixel = to_binary(image_array[i][j][k])
                    # Replace the least significant bit
                    binary_pixel = binary_pixel[:-1] + binary_secret_data[data_index]
                    # Update the pixel value
                    image_array[i][j][k] = int(binary_pixel, 2)
                    data_index += 1

    # Save the modified image
    encoded_image = Image.fromarray(image_array)
    encoded_image.save(output_path)
    return True

def decode_image(image_path):
    """Decode secret data from image using LSB steganography"""
    # Read the image
    image = Image.open(image_path)
    image_array = np.array(image)
    
    binary_data = ""
    # Extract LSB from each pixel
    for i in range(image_array.shape[0]):
        for j in range(image_array.shape[1]):
            for k in range(3):
                binary_data += to_binary(image_array[i][j][k])[-1]
    
    # Convert binary to string
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "=====":
            return decoded_data[:-5]
    
    return decoded_data