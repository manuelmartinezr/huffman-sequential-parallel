from mpi4py import MPI
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
    current_code = ''
    decoded_text = ''
    i = 0
    n = len(bit_string)
    while i < n:
        current_code += bit_string[i]
        i += 1
        if current_code in reverse_codes:
            symbol = reverse_codes[current_code]
            # Ignorar el símbolo de sincronización en la decodificación
            if ord(symbol) != 255:
                decoded_text += symbol
            current_code = ''
    return decoded_text

def decompress(file_name):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Lectura y preparación en el proceso root
    if rank == 0:
        start_time = time.time()
        binary_data, original_length, num_segments = readCompressedFile(file_name)
        bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
        bit_string = bit_string[:original_length]

        # Cargar los códigos de Huffman
        huffman_codes = np.load('huffman_codesp.npy', allow_pickle=True).item()
        synchronization_code = huffman_codes[chr(255)]

        # Dividir el flujo de bits en segmentos basados en el código de sincronización
        indices = []
        index = bit_string.find(synchronization_code)
        while index != -1:
            indices.append(index)
            index = bit_string.find(synchronization_code, index + len(synchronization_code))
        indices.append(len(bit_string))  # Añadir el final de la cadena

        # Extraer los segmentos
        segments = []
        for i in range(len(indices) - 1):
            start = indices[i] + len(synchronization_code)  # Saltar el código de sincronización
            end = indices[i + 1]
            segment = bit_string[start:end]
            segments.append(segment)

        # Distribuir los segmentos entre los procesos
        segments_per_process = [[] for _ in range(size)]
        for idx, segment in enumerate(segments):
            process_index = idx % size  # Distribuir de manera cíclica
            segments_per_process[process_index].append(segment)
    else:
        huffman_codes = None
        synchronization_code = None
        segments_per_process = None
        start_time = None

    # Difundir los códigos y el tiempo de inicio a todos los procesos
    huffman_codes = comm.bcast(huffman_codes, root=0)
    synchronization_code = comm.bcast(synchronization_code, root=0)
    start_time = comm.bcast(start_time, root=0)

    # Cada proceso recibe su lista de segmentos
    local_segments = comm.scatter(segments_per_process, root=0)

    # Decodificación local
    local_decoded = ''
    for segment in local_segments:
        local_decoded += decodeText(segment, huffman_codes)

    # Recolección de los textos decodificados
    decoded_fragments = comm.gather(local_decoded, root=0)

    if rank == 0:
        # Concatenar los fragmentos decodificados
        full_decoded_text = ''.join(decoded_fragments)

        # Escritura del archivo descomprimido
        with open('descomprimidop-ec2.txt', 'w', encoding='ISO-8859-1', newline='') as file:
            file.write(full_decoded_text)
        end_time = time.time()
        # Impresión del tiempo de ejecución
        print(f"{end_time - start_time}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        if MPI.COMM_WORLD.Get_rank() == 0:
            print("Uso: mpiexec -n <num_procesos> python descompresorp.py <archivo_comprimido>")
        sys.exit(1)
    decompress(sys.argv[1])