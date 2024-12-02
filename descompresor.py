import numpy as np
import time

import sys

def decodeText(bit_string, huffman_codes):
    reverse_codes = {v: k for k, v in huffman_codes.items()}
    current_code = ''
    decoded_text = ''
    for bit in bit_string:
        current_code += bit
        if current_code in reverse_codes:
            decoded_text += reverse_codes[current_code]
            current_code = ''
    return decoded_text

def readCompressedFile(file_name):
    with open(file_name, 'rb') as file:
        original_length = int.from_bytes(file.read(4), byteorder='big')
        binary_data = file.read()
    return binary_data, original_length

def decompress(file_name):
    start_time = time.time()
    binary_data, original_length = readCompressedFile(file_name)
    bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
    bit_string = bit_string[:original_length]
    huffman_codes = np.load('huffman_codes.npy', allow_pickle=True).item()
    decoded_text = decodeText(bit_string, huffman_codes)

    with open('descomprimido-ec2.txt', 'w', encoding='ISO-8859-1', newline='') as file:
        file.write(decoded_text)
    end_time = time.time()
    print(f"{end_time - start_time}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 descompresor.py <fileName>")
        sys.exit(1)
    file_name = sys.argv[1]
    decompress(file_name)