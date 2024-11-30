import numpy as np

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
    binary_data, original_length = readCompressedFile(file_name)
    bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
    bit_string = bit_string[:original_length]
    huffman_codes = np.load('secuencial/huffman_codes.npy', allow_pickle=True).item()
    decoded_text = decodeText(bit_string, huffman_codes)

    with open('secuencial/descomprimidop-ec2.txt', 'w', encoding='utf-8') as file:
        file.write(decoded_text)

decompress('secuencial/comprimido.ec2')