# def compress(data):
#     dict_size = 256
#     dictionary = {chr(i): i for i in range(dict_size)}
    
#     current = ""
#     result = []
#     for c in data:
#         combo = current + c
#         if combo in dictionary:
#             current = combo
#         else:
#             result.append(dictionary[current])
#             dictionary[combo] = dict_size
#             dict_size += 1
#             current = c
#     if current:
#         result.append(dictionary[current])
#     return result


# def decompress(compressed):
#     dict_size = 256
#     dictionary = {i: chr(i) for i in range(dict_size)}
    
#     result = ""
#     w = chr(compressed.pop(0))
#     result += w
#     for k in compressed:
#         if k in dictionary:
#             entry = dictionary[k]
#         elif k == dict_size:
#             entry = w + w[0]
#         else:
#             raise ValueError("Bad compressed k: %s" % k)
#         result += entry
#         dictionary[dict_size] = w + entry[0]
#         dict_size += 1
#         w = entry
#     return result


# if __name__ == "__main__":
#     sample = "TOBEORNOTTOBEORTOBEORNOT"
#     compressed = compress(sample)
#     print("Compressed:", compressed)
#     decompressed = decompress(compressed.copy())
#     print("Decompressed:", decompressed)

def compress(text):
    """
    LZW compress using UTF-8 bytes to safely handle any Unicode input.
    Returns a list of integer codes.
    """
    data = text.encode("utf-8")
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}

    current = b""
    result = []
    for byte in data:
        symbol = bytes([byte])
        combo = current + symbol
        if combo in dictionary:
            current = combo
        else:
            if current:
                result.append(dictionary[current])
            dictionary[combo] = dict_size
            dict_size += 1
            current = symbol
    if current:
        result.append(dictionary[current])
    return result


def decompress(compressed):
    """
    LZW decompress list of integer codes to text (UTF-8).
    Returns a Unicode string; undecodable bytes are replaced.
    """
    if not compressed:
        return ""
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}

    result_bytes = bytearray()
    w = bytes([compressed.pop(0)])
    result_bytes += w
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[:1]
        else:
            raise ValueError("Bad compressed k: %s" % k)
        result_bytes += entry
        dictionary[dict_size] = w + entry[:1]
        dict_size += 1
        w = entry
    return result_bytes.decode("utf-8", errors="replace")


if __name__ == "__main__":
    sample = "TOBEORNOTTOBEORTOBEORNOT"
    compressed = compress(sample)
    print("Compressed:", compressed)
    decompressed = decompress(compressed.copy())
    print("Decompressed:", decompressed)
