import sys

def readFile(file_name):
    with open(file_name, 'r') as file:
        return file.read()

def verify(file1, file2):
    text1 = readFile(file1)
    text2 = readFile(file2)
    if text1 == text2:
        print("ok")
    else:
        print("nok")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python verificador.py <file1> <file2>")
    else:
        verify(sys.argv[1], sys.argv[2])