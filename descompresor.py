import numpy as np
import time
import sys

def readCompressedFile(file_name):
    with open(file_name, 'rb') as file:
        original_length = int.from_bytes(file.read(4), byteorder='big')
        num_segments = int.from_bytes(file.read(4), byteorder='big')
        binary_data = file.read()
    return binary_data, original_length, num_segments

def decodeText(bit_string, huffman_codes):
    reverse_codes = {v: k for k, v in huffman_codes.items()}
    synchronization_code = huffman_codes[chr(255)]
    current_code = ''
    decoded_text = ''
    i = 0
    n = len(bit_string)

    # Encontrar los índices de los segmentos basados en el código de sincronización
    indices = []
    index = bit_string.find(synchronization_code)
    while index != -1:
        indices.append(index)
        index = bit_string.find(synchronization_code, index + len(synchronization_code))
    indices.append(len(bit_string))

    # Extraer y decodificar los segmentos
    for i in range(len(indices) - 1):
        start = indices[i] + len(synchronization_code)
        end = indices[i + 1]
        segment = bit_string[start:end]
        current_code = ''
        segment_decoded = ''
        j = 0
        while j < len(segment):
            current_code += segment[j]
            j += 1
            if current_code in reverse_codes:
                symbol = reverse_codes[current_code]
                if ord(symbol) != 255:
                    segment_decoded += symbol
                current_code = ''
        decoded_text += segment_decoded
    return decoded_text

def decompress(file_name):
    start_time = time.time()
    binary_data, original_length, num_segments = readCompressedFile(file_name)
    bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
    bit_string = bit_string[:original_length]
    if file_name == 'comprimido.ec2':
        huffman_codes = np.load('huffman_codes.npy', allow_pickle=True).item()
    else:
        huffman_codes = np.load('huffman_codesp.npy', allow_pickle=True).item()
    decoded_text = decodeText(bit_string, huffman_codes)

    with open('descomprimido-ec2.txt', 'w', encoding='ISO-8859-1', newline='') as file:
        file.write(decoded_text)
    end_time = time.time()
    print(f"{end_time - start_time}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 descompresor.py <archivo_comprimido>")
        sys.exit(1)
    file_name = sys.argv[1]
    decompress(file_name)