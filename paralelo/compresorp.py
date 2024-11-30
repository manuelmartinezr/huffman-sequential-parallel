from mpi4py import MPI
import numpy as np
import time
import sys
import heapq

class Node:
    def __init__(self, symbol=None, frequency=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None

    # Necesario para la cola de prioridad
    def __lt__(self, other):
        return self.frequency < other.frequency

def huffmanTree(chars, freqs):
    priority_queue = [Node(char, freq) for char, freq in zip(chars, freqs)]
    heapq.heapify(priority_queue)
    while len(priority_queue) > 1:
        left_child = heapq.heappop(priority_queue)
        right_child = heapq.heappop(priority_queue)
        merged_node = Node(frequency=left_child.frequency + right_child.frequency)
        merged_node.left = left_child
        merged_node.right = right_child
        heapq.heappush(priority_queue, merged_node)
    return priority_queue[0]

def huffmanCodes(node, code="", huffman_codes=None):
    if huffman_codes is None:
        huffman_codes = {}
    if node.symbol is not None:
        huffman_codes[node.symbol] = code
    else:
        huffmanCodes(node.left, code + "0", huffman_codes)
        huffmanCodes(node.right, code + "1", huffman_codes)
    return huffman_codes

def textToString(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print("Error: archivo no encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        sys.exit(1)

def charFrequencies(text):
    char_to_freq = {}
    for char in text:
        char_to_freq[char] = char_to_freq.get(char, 0) + 1
    return char_to_freq

def writeToCompressed(data, original_length):
    output_file = 'paralelo/comprimidop.ec2'
    binary_data = bytearray()
    for i in range(0, len(data), 8):
        byte = data[i:i+8]
        if len(byte) < 8:
            byte = byte.ljust(8, '0')  # Rellenar con ceros si es necesario
        binary_data.append(int(byte, 2))
    with open(output_file, 'wb') as file:
        file.write(original_length.to_bytes(4, byteorder='big'))
        file.write(binary_data)

def compress(file_name):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Lectura y distribución del texto
    if rank == 0:
        start_time = time.time()
        text = textToString(file_name)
        text_length = len(text)
        # Calcular los tamaños de cada fragmento
        chunk_sizes = [text_length // size] * size
        for i in range(text_length % size):
            chunk_sizes[i] += 1
        # Dividir el texto en fragmentos
        chunks = []
        index = 0
        for size_chunk in chunk_sizes:
            chunks.append(text[index:index+size_chunk])
            index += size_chunk
    else:
        chunks = None

    # Distribuir los fragmentos de texto a cada proceso
    local_text = comm.scatter(chunks, root=0)

    # Cálculo de frecuencias locales
    local_freq = charFrequencies(local_text)

    # Recolección de frecuencias locales en el root
    all_freqs = comm.gather(local_freq, root=0)

    if rank == 0:
        # Combinación de frecuencias
        combined_freq = {}
        for freq_dict in all_freqs:
            for char, count in freq_dict.items():
                combined_freq[char] = combined_freq.get(char, 0) + count

        # Construcción del árbol de Huffman y códigos
        chars = list(combined_freq.keys())
        freqs = list(combined_freq.values())
        root_node = huffmanTree(chars, freqs)
        huffman_codes = huffmanCodes(root_node)

        # Guardado de los códigos de Huffman
        np.save('paralelo/huffman_codes.npy', huffman_codes)
    else:
        huffman_codes = None

    # Broadcast de los códigos de Huffman
    huffman_codes = comm.bcast(huffman_codes, root=0)

    # Codificación local
    local_encoded = ''.join(huffman_codes[char] for char in local_text)
    local_encoded_bytes = np.frombuffer(local_encoded.encode('ascii'), dtype='B')
    local_encoded_size = np.array(len(local_encoded_bytes), dtype='i')

    # Recolección de tamaños codificados
    encoded_sizes = comm.gather(local_encoded_size, root=0)

    if rank == 0:
        total_encoded_size = sum(encoded_sizes)
        encoded_data = np.empty(total_encoded_size, dtype='B')
        displacements = np.zeros(size, dtype='i')
        displacements[1:] = np.cumsum(encoded_sizes[:-1])
    else:
        encoded_data = None
        displacements = None

    # Recolección de datos codificados usando Gatherv
    comm.Gatherv(local_encoded_bytes, [encoded_data, encoded_sizes, displacements, MPI.BYTE], root=0)

    if rank == 0:
        # Convertir los datos recolectados a string
        full_encoded_data = encoded_data.tobytes().decode('ascii')

        # Escritura del archivo comprimido
        writeToCompressed(full_encoded_data, len(full_encoded_data))
        end_time = time.time()
        # Imprimir el tiempo de ejecución
        print(f"{end_time - start_time}")
    # Fin de la función compress

if __name__ == "__main__":
    if len(sys.argv) != 2:
        if MPI.COMM_WORLD.Get_rank() == 0:
            print("Uso: mpiexec -n <num_procesos> python compresorp.py <archivo_txt>")
        sys.exit(1)
    compress(sys.argv[1])