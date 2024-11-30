from mpi4py import MPI
import numpy as np
import time
import sys

def readCompressedFile(file_name):
    with open(file_name, 'rb') as file:
        original_length = int.from_bytes(file.read(4), byteorder='big')
        binary_data = file.read()
    return binary_data, original_length

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

def decompress(file_name):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        start_time = time.time()
        binary_data, original_length = readCompressedFile(file_name)
        bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
        bit_string = bit_string[:original_length]
        huffman_codes = np.load('paralelo/huffman_codes.npy', allow_pickle=True).item()

        # Decodificación completa en el proceso raíz
        decoded_text = decodeText(bit_string, huffman_codes)

        # Escritura del archivo descomprimido
        with open('paralelo/descomprimidop-ec2.txt', 'w', encoding='utf-8') as file:
            file.write(decoded_text)
        end_time = time.time()
        # Impresión del tiempo de ejecución
        print(f"{end_time - start_time}")
    else:
        # Otros procesos no hacen nada
        pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        if MPI.COMM_WORLD.Get_rank() == 0:
            print("Uso: mpiexec -n <num_procesos> python descompresorp.py <archivo_comprimido>")
        sys.exit(1)
    decompress(sys.argv[1])