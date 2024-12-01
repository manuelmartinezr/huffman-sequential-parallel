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
            if ord(symbol) != 257:
                decoded_text += symbol
            current_code = ''
    return decoded_text

def decompress(file_name):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Lectura y distribución del flujo de bits comprimido
    if rank == 0:
        start_time = time.time()
        binary_data, original_length, num_segments = readCompressedFile(file_name)
        bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
        bit_string = bit_string[:original_length]

        # Cargar los códigos de Huffman
        huffman_codes = np.load('huffman_codes.npy', allow_pickle=True).item()
        synchronization_code = huffman_codes[chr(257)]
        # Dividir el flujo de bits en segmentos basados en el código de sincronización
        # Encontrar las posiciones de los marcadores
        indices = []
        index = bit_string.find(synchronization_code)
        while index != -1:
            indices.append(index)
            index = bit_string.find(synchronization_code, index + len(synchronization_code))
        # Añadir el final de la cadena
        indices.append(len(bit_string))

        # Extraer los segmentos
        segments = []
        for i in range(len(indices) - 1):
            start = indices[i]
            end = indices[i+1]
            # Excluir el marcador del segmento
            segment = bit_string[start:end]
            segments.append(segment)
    else:
        huffman_codes = None
        segments = None
        synchronization_code = None
        start_time = None

    # Broadcast de los códigos de Huffman y el símbolo de sincronización
    huffman_codes = comm.bcast(huffman_codes, root=0)
    synchronization_code = comm.bcast(synchronization_code, root=0)
    start_time = comm.bcast(start_time, root=0)

    # Distribuir los segmentos a los procesos
    local_segment = comm.scatter(segments, root=0)

    # Decodificación local
    local_decoded = decodeText(local_segment, huffman_codes)

    # Recolección de los textos decodificados
    decoded_fragments = comm.gather(local_decoded, root=0)

    if rank == 0:
        # Concatenar los fragmentos decodificados
        full_decoded_text = ''.join(decoded_fragments)

        # Escritura del archivo descomprimido
        with open('descomprimidop-ec2.txt', 'w', encoding='utf-8') as file:
            file.write(full_decoded_text)
        end_time = time.time()
        # Impresión del tiempo de ejecución
        print(f"{end_time - start_time}")
    # Fin de la función decompress

if __name__ == "__main__":
    if len(sys.argv) != 2:
        if MPI.COMM_WORLD.Get_rank() == 0:
            print("Uso: mpiexec -n <num_procesos> python descompresorp.py <archivo_comprimido>")
        sys.exit(1)
    decompress(sys.argv[1])