def compress(data):
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}
    
    current = ""
    result = []
    for c in data:
        combo = current + c
        if combo in dictionary:
            current = combo
        else:
            result.append(dictionary[current])
            dictionary[combo] = dict_size
            dict_size += 1
            current = c
    if current:
        result.append(dictionary[current])
    return result


def decompress(compressed):
    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)}
    
    result = ""
    w = chr(compressed.pop(0))
    result += w
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            raise ValueError("Bad compressed k: %s" % k)
        result += entry
        dictionary[dict_size] = w + entry[0]
        dict_size += 1
        w = entry
    return result


if __name__ == "__main__":
    sample = "TOBEORNOTTOBEORTOBEORNOT"
    compressed = compress(sample)
    print("Compressed:", compressed)
    decompressed = decompress(compressed.copy())
    print("Decompressed:", decompressed)
