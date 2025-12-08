import math


def unary_encode(n):
    return '1' * n + '0'


def unary_decode(code):
    count = 0
    for c in code:
        if c == '1':
            count += 1
        else:
            break
    return count


def to_binary(n, bits):
    return format(n, '0{}b'.format(bits))


def from_binary(b):
    return int(b, 2)


def compress(data, m=5):
    result = ""
    for char in data:
        num = ord(char)
        q = num // m
        r = num % m
        bits = math.ceil(math.log2(m))
        result += unary_encode(q) + to_binary(r, bits)
    return result


def decompress(compressed, m=5):
    i = 0
    result = ""
    bits = math.ceil(math.log2(m))
    while i < len(compressed):
        q = 0
        while compressed[i] == '1':
            q += 1
            i += 1
        i += 1
        r = from_binary(compressed[i:i + bits])
        i += bits
        result += chr(q * m + r)
    return result


if __name__ == "__main__":
    sample = "HELLO"
    compressed = compress(sample)
    print("Compressed:", compressed)
    print("Decompressed:", decompress(compressed))
