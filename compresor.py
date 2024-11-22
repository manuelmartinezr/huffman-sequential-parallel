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

txt = "AAA BBC"
char_to_freq = charFrequencies(txt)
print(char_to_freq)
keys = list(char_to_freq.keys())
values = list(char_to_freq.values())
root = huffmanTree(keys, values)
huffman_codes = huffmanCodes(root)
for char, code in huffman_codes.items():
    print(f"Character:{char}, code:{code}")

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

print(codeText(txt, huffman_codes))
print(decodeText(codeText(txt, huffman_codes), huffman_codes))