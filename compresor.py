import sys
import numpy as np
import time
import heapq

class Node:
    def __init__(self, symbol=None, frequency=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency

def huffmanTree(chars, freq):
    priority_queue = [Node(char, f) for char, f in zip(chars, freq)]
    heapq.heapify(priority_queue)
    while len(priority_queue) > 1:
        left_child = heapq.heappop(priority_queue)
        right_child = heapq.heappop(priority_queue)
        merged_node = Node(frequency=left_child.frequency + right_child.frequency)
        merged_node.left = left_child
        merged_node.right = right_child
        heapq.heappush(priority_queue, merged_node)
    return priority_queue[0]

def huffmanCodes(node, code="", huffman_codes={}):
    if node is not None:
        if node.symbol is not None:
            huffman_codes[node.symbol] = code
        huffmanCodes(node.left, code + "0", huffman_codes)
        huffmanCodes(node.right, code + "1", huffman_codes)
    return huffman_codes

def charFrequencies(text):
    char_to_freq = {}
    for char in text:
        char_to_freq[char] = char_to_freq.get(char, 0) + 1
    return char_to_freq

def codeText(text, huffman_codes):
    coded = ''
    for char in text:
        coded += huffman_codes[char]
    return coded

def textToString(file_name):
    with open(file_name, 'r', encoding='ISO-8859-1', newline='') as file:
        return file.read()

def writeToCompressed(data, original_length, num_segments):
    output_file = 'comprimido.ec2'
    binary_data = bytearray()
    for i in range(0, len(data), 8):
        byte = data[i:i+8]
        if len(byte) < 8:
            byte = byte.ljust(8, '0')
        binary_data.append(int(byte, 2))
    with open(output_file, 'wb') as file:
        file.write(original_length.to_bytes(4, byteorder='big'))
        file.write(num_segments.to_bytes(4, byteorder='big'))
        file.write(binary_data)

def compress(file_name):
    try:
        start_time = time.time()
        text = textToString(file_name)

        # Añadir símbolo de sincronización al inicio
        synchronization_symbol = chr(255)
        text = synchronization_symbol + text

        char_to_freq = charFrequencies(text)
        # Asegurar que el símbolo de sincronización tenga una frecuencia mínima
        char_to_freq[synchronization_symbol] = char_to_freq.get(synchronization_symbol, 1)

        keys = list(char_to_freq.keys())
        values = list(char_to_freq.values())
        root = huffmanTree(keys, values)
        huffman_codes = huffmanCodes(root)
        np.save('huffman_codes.npy', huffman_codes)
        data = codeText(text, huffman_codes)

        # Definir el número de segmentos (en este caso, 1)
        num_segments = 1

        writeToCompressed(data, len(data), num_segments)
        end_time = time.time()
        print(f"{end_time - start_time}")
    except Exception as e:
        print(f"Ocurrió un error durante la compresión: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 compresor.py <archivo_txt>")
        sys.exit(1)
    file_name = sys.argv[1]
    compress(file_name)