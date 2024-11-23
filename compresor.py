# import sys

# if len(sys.argv) < 2:
#     print("Usage: python3 compresor.py <fileName>")
#     sys.exit(1)

# file_name = sys.argv[1]

# try:
#     with open(file_name, 'r') as file:
#         content = file.read()
# except FileNotFoundError:
#     print(f"Error: File '{file_name}' not found.")

# Python program for Huffman Coding
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
  
    # Create a priority queue of nodes
    priority_queue = [Node(char, f) for char, f in zip(chars, freq)]
    heapq.heapify(priority_queue)

    # Build the Huffman tree
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
        if char not in char_to_freq:
            char_to_freq[char] = 1
        else:
            char_to_freq[char] += 1
    return char_to_freq

def codeText(text, huffman_codes):
    coded = ""
    for char in text:
        code = huffman_codes[char]
        coded += code
    return coded

def decodeText(text, huffman_codes):
    chars = {v:k for k, v in huffman_codes.items()}
    decoded = ""
    temp_code = ""
    for code in text:
        temp_code += code
        if temp_code in chars:
            char = chars[temp_code]
            decoded += char
            temp_code = ""
    return decoded

def textToString(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:  # Open the file in read mode with UTF-8 encoding
            return file.read()  # Read the entire file content into a string
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"An error occurred: {e}"

def writeToComprimido(string_data):
    # Define the output file name
    output_file = 'comprimido.ec2'

    # Ensure the string_data is a valid binary string (only '1' and '0')
    if not all(bit in '01' for bit in string_data):
        raise ValueError("The input string contains invalid characters. Only '1' and '0' are allowed.")

    # Convert the binary string into a byte array (no padding)
    binary_data = bytearray()

    # Iterate over the bit string in chunks of 8 bits (1 byte each)
    for i in range(0, len(string_data), 8):
        byte = string_data[i:i + 8]  # Take the next 8 bits
        if len(byte) < 8:
            # If the byte is smaller than 8 bits, it's fine to leave it as it is, no padding here
            byte = byte.ljust(8, '0')  # This could be avoided if you want exact bits
        # Convert the 8-bit string to an integer and append it as byte
        binary_data.append(int(byte, 2))

    # Open the file in write binary mode ('wb') to write the data as bytes
    with open(output_file, 'wb') as file:
        file.write(binary_data)

    print(f"Data has been written to {output_file}")

def compress(file_name):
    text = textToString(file_name)
    char_to_freq = charFrequencies(text)
    keys = list(char_to_freq.keys())
    values = list(char_to_freq.values())
    root = huffmanTree(keys, values)
    huffman_codes = huffmanCodes(root)
    data = codeText(text, huffman_codes)
    writeToComprimido(data)

compress('text1.txt')
