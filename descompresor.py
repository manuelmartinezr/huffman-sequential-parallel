def decodeText(text, huffman_codes):
    code = ''
    decoded = ''
    i = 0
    reverse_huffman_codes = {v: k for k, v in huffman_codes.items()}
    while i < len(text):
        char = text[i]
        code += char
        if code in reverse_huffman_codes:
            decoded += reverse_huffman_codes[code]
            i += 8 - len(code)
            code = ''
        else:
            i += 1
    return decoded
